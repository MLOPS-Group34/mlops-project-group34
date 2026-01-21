"""
Inference Dashboard - Generate and view prediction grids.
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

st.set_page_config(
    page_title="Inference Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "current_grid" not in st.session_state:
    st.session_state.current_grid = 1
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "generation_complete" not in st.session_state:
    st.session_state.generation_complete = False

# Title
st.title("🔥 Inference Dashboard")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    config_path = st.text_input(
        "Config Path",
        value="configs/config.yaml",
        help="Path to the YAML config file"
    )
    
    st.divider()
    st.subheader("About")
    st.markdown(
        """
        This dashboard displays prediction grids from your trained YOLO model.
        
        **Features:**
        - View top 24 predictions (4 grids of 6 images each)
        - Navigate through different prediction grids
        - Generate new samples with a single click
        - Images sorted by confidence score
        
        **Legend:**
        - 🟢 Green boxes = Ground Truth
        - 🔴 Red boxes = Predictions
        """
    )

# Main content
tab1, tab2 = st.tabs(["📸 Prediction Gallery", "⚙️ Generate New Samples"])

with tab1:
    st.header("Prediction Grids")
    
    # Import visualization function
    from forestfires_project.visualize import run_visualization
    
    # Get available grid images
    reports_dir = project_root / "reports" / "figures"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Grid", f"{st.session_state.current_grid}/4")
    with col2:
        # Count available grids
        grid_files = sorted([f for f in reports_dir.glob("predictions_grid_*.png")])
        st.metric("Available Grids", len(grid_files))
    with col3:
        st.metric("Images per Grid", "6")
    
    st.divider()
    
    # Display grid image
    if len(grid_files) > 0:
        grid_idx = st.session_state.current_grid - 1
        
        if grid_idx < len(grid_files):
            grid_path = grid_files[grid_idx]
            st.image(
                str(grid_path),
                caption=f"Prediction Grid {st.session_state.current_grid} - Top 6 Predictions by Confidence",
                width='stretch',
            )
            
            # Navigation buttons
            nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
            
            with nav_col1:
                if st.button("⬅️ Previous Grid", use_container_width=True):
                    if st.session_state.current_grid > 1:
                        st.session_state.current_grid -= 1
                        st.rerun()
            
            with nav_col2:
                st.write("")  # Spacer
            
            with nav_col3:
                st.write("")  # Spacer
            
            with nav_col4:
                if st.button("Next Grid ➡️", use_container_width=True):
                    if st.session_state.current_grid < len(grid_files):
                        st.session_state.current_grid += 1
                        st.rerun()
            
            # Grid selector
            st.divider()
            selected_grid = st.slider(
                "Select Grid",
                min_value=1,
                max_value=len(grid_files),
                value=st.session_state.current_grid,
                step=1,
            )
            if selected_grid != st.session_state.current_grid:
                st.session_state.current_grid = selected_grid
                st.rerun()
        else:
            st.warning("Grid not found. Generate new samples to populate the gallery.")
    else:
        st.info("📂 No prediction grids found. Click 'Generate New Samples' to create them!")

with tab2:
    st.header("Generate New Prediction Grids")
    
    st.markdown(
        """
        Click the button below to run inference on the test set and generate new prediction grids.
        
        **What happens:**
        1. Model loads the trained weights
        2. Inference runs on all test images
        3. Top 24 predictions (by confidence) are selected
        4. 4 grid visualizations are created (6 images each)
        5. Results are saved to `reports/figures/`
        
        **Note:** This may take a few minutes depending on your hardware.
        """
    )
    
    st.divider()
    
    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button(
            "🚀 Generate New Samples",
            use_container_width=True,
            disabled=st.session_state.is_generating,
            key="generate_btn",
        ):
            st.session_state.is_generating = True
            st.rerun()
    
    # Processing logic
    if st.session_state.is_generating:
        try:
            with st.spinner("🔄 Running inference and generating prediction grids..."):
                # Run visualization
                run_visualization(config_path=config_path)
            
            st.session_state.is_generating = False
            st.session_state.generation_complete = True
            st.session_state.current_grid = 1  # Reset to first grid
            
            st.success("✅ Prediction grids generated successfully!")
            st.balloons()
            st.rerun()
        
        except FileNotFoundError as e:
            st.session_state.is_generating = False
            st.error(f"❌ File not found: {str(e)}")
            st.info("Make sure your config path is correct and model weights exist.")
        
        except Exception as e:
            st.session_state.is_generating = False
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Check the console for more details or verify your setup.")
    
    # Info box
    if st.session_state.generation_complete:
        st.info("Generation completed! Check the 'Prediction Gallery' tab to view results.")
