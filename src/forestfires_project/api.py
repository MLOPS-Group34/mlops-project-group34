from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from ultralytics import YOLO
from PIL import Image
import io
import torch
from fastapi.responses import StreamingResponse
import numpy as np
import cv2
import psutil

app = FastAPI(title="YOLO Inference API")

MODEL_PATH = "models/forest_fire_detection/weights/best.pt"

# Load YOLO model once at startup
try:
    yolo = YOLO(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load YOLO model from {MODEL_PATH}: {e}")


@app.get("/")
def read_root():
    return {"message": "YOLO Inference API is running", "model_path": MODEL_PATH}


@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Image file (jpg/png/etc.)"),
    conf: float = Query(0.25, ge=0.0, le=1.0, description="Confidence threshold"),
    iou: float = Query(0.7, ge=0.0, le=1.0, description="IoU threshold (NMS)"),
    max_det: int = Query(300, ge=1, le=3000, description="Max detections per image"),
):
    try:
        # Read and decode image
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

        # Run inference
        # Ultralytics handles preprocessing internally
        results = yolo.predict(
            source=img,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False,
        )

        # results is a list (one per image)
        r = results[0]

        # Classes map (id -> name)
        names = r.names if hasattr(r, "names") else getattr(yolo.model, "names", {})

        detections = []

        # r.boxes is an ultralytics Boxes object
        if r.boxes is not None and len(r.boxes) > 0:
            # xyxy, conf, cls are torch tensors
            xyxy = r.boxes.xyxy
            confs = r.boxes.conf
            clss = r.boxes.cls

            # Move to CPU and convert to python types safely
            xyxy = xyxy.detach().cpu().tolist()
            confs = confs.detach().cpu().tolist()
            clss = clss.detach().cpu().tolist()

            for box, score, cls_id in zip(xyxy, confs, clss):
                cls_int = int(cls_id)
                detections.append(
                    {
                        "class_id": cls_int,
                        "class_name": names.get(cls_int, str(cls_int)) if isinstance(names, dict) else str(cls_int),
                        "confidence": float(score),
                        "box_xyxy": [float(v) for v in box],  # [x1, y1, x2, y2]
                    }
                )

        # Optional: include speed info if present
        speed = getattr(r, "speed", None)

        return {
            "filename": file.filename,
            "image_size": {"width": img.width, "height": img.height},
            "conf": conf,
            "iou": iou,
            "max_det": max_det,
            "num_detections": len(detections),
            "detections": detections,
            "speed": speed,  # may be None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


@app.get("/device")
def device_info():
    return {
        "torch_cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
    }


@app.post("/predict/image")
async def predict_image(
    file: UploadFile = File(...),
    conf: float = Query(0.25, ge=0.0, le=1.0),
    iou: float = Query(0.7, ge=0.0, le=1.0),
    max_det: int = Query(300, ge=1, le=3000),
):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        # Load image
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Run YOLO
        results = yolo.predict(
            source=pil_img,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False,
        )
        r = results[0]
        names = r.names

        # Draw boxes
        if r.boxes is not None:
            for box, score, cls_id in zip(r.boxes.xyxy, r.boxes.conf, r.boxes.cls):
                x1, y1, x2, y2 = map(int, box.tolist())
                cls_id = int(cls_id)
                label = f"{names[cls_id]} {score:.2f}"

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    img,
                    label,
                    (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

        # Encode image to JPEG
        _, encoded = cv2.imencode(".jpg", img)

        return StreamingResponse(
            io.BytesIO(encoded.tobytes()),
            media_type="image/jpeg",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def get_system_metrics():
    try:
        metrics = {
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent,
            },
            "uptime_seconds": psutil.boot_time(),
        }
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {e}")
