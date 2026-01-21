# 🔥 Streamlit Dashboard - Visual Architecture & Workflow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    🔥 STREAMLIT DASHBOARD 🔥                    │
│              Forest Fire Detection Visualization                 │
└─────────────────────────────────────────────────────────────────┘

                         Browser (localhost:8501)
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
              Sidebar                        Main Content
              ────────                       ────────────
              • Config Path      Tab 1: 📸 Prediction Gallery
              • Info Panel        ├─ Metrics
              • Settings          ├─ Image Display
                                 ├─ Navigation
                                 └─ Grid Selector
                                
                                Tab 2: ⚙️ Generate Samples
                                 ├─ Instructions
                                 ├─ Generate Button
                                 └─ Status Display
                                
                                Page: 📊 Performance
                                 └─ Stats & Info


┌─────────────────────────────────────────────────────────────────┐
│                      Application Flow                            │
└─────────────────────────────────────────────────────────────────┘

  USER ACTION              STREAMLIT APP                BACKEND
  ───────────              ──────────                   ───────
  
  1. Start Dashboard   →   streamlit_app.py          ↓
                          ├─ Load config
                          ├─ Initialize state
                          └─ Display UI
  
  2. View Predictions  →   Prediction Gallery Tab   →  reports/figures/
                          ├─ Load PNG files
                          ├─ Display image
                          └─ Show navigation
  
  3. Navigate Grids   →   Session State Manager     →  N/A
                          ├─ Update current_grid
                          └─ Refresh display
  
  4. Click Generate   →   Generate New Samples    →   Model + Data
                          ├─ Show spinner
                          ├─ Call run_visualization()
                          ├─ Load model weights
                          ├─ Run inference
                          ├─ Generate grids
                          └─ Save PNG files
  
  5. View New Grids   →   Gallery refreshes       →   reports/figures/


┌─────────────────────────────────────────────────────────────────┐
│                   File Structure Flow                            │
└─────────────────────────────────────────────────────────────────┘

   streamlit_app.py (Main Entry Point)
           │
           ├─→ .streamlit/config.toml (Settings)
           │
           ├─→ forestfires_project/visualize.py
           │   ├─→ ForestFireYOLO (model loading)
           │   ├─→ get_test_loader (data loading)
           │   └─→ Generate PNGs
           │
           ├─→ forestfires_project/utils.py (Helpers)
           │   ├─→ get_prediction_grids()
           │   └─→ get_grid_info()
           │
           ├─→ configs/config.yaml (Configuration)
           │   ├─→ Model path
           │   ├─→ Data path
           │   └─→ Output path
           │
           └─→ reports/figures/
               └─→ predictions_grid_*.png


┌─────────────────────────────────────────────────────────────────┐
│                    Data Flow Diagram                             │
└─────────────────────────────────────────────────────────────────┘

  PREDICTION GENERATION PIPELINE
  ──────────────────────────────
  
  Test Data (YOLO format)
         ↓
  Load via get_test_loader()
         ↓
  ForestFireYOLO.predict()  [Inference]
         ↓
  Extract predictions (boxes, confidence)
         ↓
  Calculate avg_conf per image
         ↓
  Sort all results by confidence
         ↓
  Select top 24 results
         ↓
  Create 4 grids (6 images each)
         ↓
  Draw boxes (GT + Predictions)
         ↓
  Save as PNG files
         ↓
  reports/figures/predictions_grid_*.png


  GALLERY DISPLAY PIPELINE
  ────────────────────────
  
  reports/figures/
         ↓
  Streamlit loads PNG files
         ↓
  st.image() displays image
         ↓
  Navigation updates current_grid
         ↓
  Browser refreshes display
         ↓
  User views predictions


┌─────────────────────────────────────────────────────────────────┐
│                  Component Interaction Map                       │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │  User Interface │
  │  (Streamlit UI) │
  └────────┬────────┘
           │
    ┌──────┴─────────┐
    │                │
    v                v
┌────────┐      ┌─────────┐
│ Sidebar│      │  Tabs   │
└────┬───┘      └────┬────┘
     │               │
     │         ┌─────┴──────┬────────────┐
     │         │            │            │
     v         v            v            v
┌────────┐ ┌────────────┐ ┌─────────┐ ┌────────┐
│ Config │ │ Gallery    │ │Generate │ │ Info   │
│ Input  │ │ (Displays) │ │(Runs)   │ │(Shows) │
└────┬───┘ └────┬───────┘ └────┬────┘ └────────┘
     │         │              │
     │         └──────┬───────┘
     │                │
     v                v
┌──────────────────────────────┐
│   Session State Manager      │
│  (Tracks UI state)           │
│  - current_grid              │
│  - is_generating             │
│  - generation_complete       │
└──────────┬───────────────────┘
           │
     ┌─────┴────────────────────┬─────────────┐
     │                          │             │
     v                          v             v
┌──────────────┐      ┌──────────────────┐  ┌────────────┐
│ Visualization│      │  Model Loading   │  │ Config     │
│ Module       │      │  & Inference     │  │ Parsing    │
└──────┬───────┘      └────────┬─────────┘  └────────┬───┘
       │                       │                     │
       │         ┌─────────────┴──────────┐          │
       │         │                        │          │
       v         v                        v          v
   ┌─────────────────────────────────────────────────┐
   │         Filesystem & Resources                  │
   ├─────────────────────────────────────────────────┤
   │ • configs/config.yaml (read)                    │
   │ • models/{model_name}/weights/best.pt (read)   │
   │ • data/processed/test/ (read)                  │
   │ • reports/figures/predictions_grid_*.png (r/w) │
   └─────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│               User Journey Through Dashboard                     │
└─────────────────────────────────────────────────────────────────┘

  START
    ↓
  [1] User runs: streamlit run app/streamlit_app.py
    ↓
  [2] Browser opens dashboard (localhost:8501)
    ↓
  [3] Dashboard checks for prediction grids
    ├─ NO: "No grids found" message
    └─ YES: Display first grid
    ↓
  [4] User clicks "Generate New Samples" (first time)
    ↓
  [5] Model loads & inference runs (~2-10 min)
    ├─ Progress: Spinner shows
    ├─ Processing: Visualization generates
    └─ Completion: Success message + balloons 🎉
    ↓
  [6] Auto-navigates to Gallery tab
    ↓
  [7] User browses predictions
    ├─ Previous/Next buttons
    ├─ Slider for quick jump
    └─ View confidence scores
    ↓
  [8] Optional: Generate new samples again
    └─ Repeats from step [4]
    ↓
  CONTINUE ANALYZING


┌─────────────────────────────────────────────────────────────────┐
│                    Key Design Decisions                          │
└─────────────────────────────────────────────────────────────────┘

  1. SINGLE FILE ENTRY POINT
     Why: Simple to run, easy to understand
     How: app/streamlit_app.py contains all UI logic

  2. SESSION STATE MANAGEMENT
     Why: Track UI state without reloading
     What: current_grid, is_generating, generation_complete
     Benefit: Smooth UX, no data loss on interaction

  3. TWO-TAB ARCHITECTURE
     Why: Separate concerns (view vs. action)
     Gallery: Read/browse predictions
     Generate: Write/create new predictions

  4. ERROR HANDLING
     Why: Graceful failure, user guidance
     How: Try/except blocks, informative error messages

  5. CONFIGURATION FLEXIBILITY
     Why: Users can customize without code changes
     How: Sidebar input for config path, editable settings

  6. DIRECT FUNCTION IMPORT
     Why: Reuse existing visualization code
     How: Import run_visualization() directly from module

  7. ASYNC-STYLE FEEDBACK
     Why: Better UX during long operations
     How: Spinner + status messages during generation


┌─────────────────────────────────────────────────────────────────┐
│                  Performance Optimization                        │
└─────────────────────────────────────────────────────────────────┘

  IMAGE LOADING
  ├─ PNG format (efficient)
  ├─ Direct file read (no processing)
  └─ Cached by browser

  MODEL INFERENCE
  ├─ YOLOv8n (small model, ~6MB)
  ├─ Optimized for speed
  └─ CPU-compatible

  UI RENDERING
  ├─ Minimal state changes
  ├─ Efficient layout (Streamlit columns)
  └─ No unnecessary reruns

  SESSION PERSISTENCE
  ├─ State survives UI interactions
  └─ No data reload needed


┌─────────────────────────────────────────────────────────────────┐
│                    File Dependencies                             │
└─────────────────────────────────────────────────────────────────┘

  CRITICAL (Must exist to run)
  ├─ app/streamlit_app.py (main app)
  ├─ .streamlit/config.toml (settings)
  ├─ configs/config.yaml (config)
  └─ src/forestfires_project/ (model code)

  IMPORTANT (Needed for full functionality)
  ├─ models/{model}/weights/best.pt (model)
  └─ data/processed/test/ (test data)

  OPTIONAL (Nice to have)
  ├─ reports/figures/ (grid storage)
  └─ Documentation files

  GENERATED (Created by dashboard)
  └─ reports/figures/predictions_grid_*.png


┌─────────────────────────────────────────────────────────────────┐
│                   Deployment Readiness                           │
└─────────────────────────────────────────────────────────────────┘

  ✅ READY FOR:
     - Local development
     - Desktop testing
     - Team demonstrations
     - Model evaluation
     - Results visualization

  ⚠️  CONSIDERATIONS FOR PRODUCTION:
     - Add authentication (if multi-user)
     - Use persistent storage (not local)
     - Add monitoring/logging
     - Scale model inference (batching, GPU)
     - Version grids with timestamps

---

**This architecture provides a clean, maintainable, and user-friendly
interface to your forest fire detection model!**
