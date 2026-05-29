def get_custom_css() -> str:
    """
    Generates and returns the premium custom CSS design system rules for styling
    Streamlit layout elements, sidebar widgets, input elements, multiselect chips,
    and visual card wrappers based on the Glassmorphic Cosmic Dark theme.

    Returns:
        str: HTML style tag block containing raw CSS overrides.
    """
    return """
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global settings overrides */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #06060c !important;
        color: #f0f3f8 !important;
    }

    /* Main container padding and max width */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* Custom thin scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.01);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(77, 163, 255, 0.2);
    }

    /* Sidebar background and border */
    [data-testid="stSidebar"] {
        background-color: #0a0b14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        font-size: 0.95rem !important;
        color: #4da3ff !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1.25rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 700 !important;
        opacity: 0.9;
    }
    
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        font-weight: 600 !important;
        color: #8b9bb4 !important;
        font-size: 0.85rem !important;
    }
    
    /* App Title Gradient (Sleek Cosmic Glow) */
    h1 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #00f2fe 0%, #4da3ff 35%, #a25eff 70%, #ff5e97 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
        margin-bottom: 1.5rem !important;
        text-shadow: 0 0 50px rgba(77, 163, 255, 0.1);
    }
    
    h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700 !important;
        color: #f0f3f8 !important;
        letter-spacing: -0.02em;
    }

    /* Style native Streamlit metric cards & container borders */
    [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.7) 0%, rgba(13, 14, 28, 0.7) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 18px !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-testid="stMetric"]:hover, [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) scale(1.01) !important;
        background: rgba(22, 23, 42, 0.8) !important;
        border-color: rgba(77, 163, 255, 0.15) !important;
    }

    /* Custom Branded Cards */
    .custom-card {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.7) 0%, rgba(13, 14, 28, 0.7) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 18px !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 110px;
    }
    .custom-card:hover {
        transform: translateY(-4px) scale(1.01) !important;
        background: rgba(22, 23, 42, 0.8) !important;
        border-color: rgba(77, 163, 255, 0.15) !important;
    }
    .card-blue {
        border-left: 4px solid #4da3ff !important;
    }
    .card-blue:hover {
        box-shadow: 0 12px 35px 0 rgba(77, 163, 255, 0.15) !important;
    }
    .card-purple {
        border-left: 4px solid #a25eff !important;
    }
    .card-purple:hover {
        box-shadow: 0 12px 35px 0 rgba(162, 94, 255, 0.15) !important;
    }
    .card-pink {
        border-left: 4px solid #ff5e97 !important;
    }
    .card-pink:hover {
        box-shadow: 0 12px 35px 0 rgba(255, 94, 151, 0.15) !important;
    }
    .card-label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #8b9bb4 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .card-value {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .badge-neutral {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #8b9bb4 !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        display: inline-block;
    }

    /* Distinct glows and left borders for metric cards */
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {
        border-left: 4px solid #4da3ff !important;
    }
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"]:hover {
        border-color: #4da3ff !important;
        box-shadow: 0 12px 35px 0 rgba(77, 163, 255, 0.15) !important;
    }

    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
        border-left: 4px solid #a25eff !important;
    }
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"]:hover {
        border-color: #a25eff !important;
        box-shadow: 0 12px 35px 0 rgba(162, 94, 255, 0.15) !important;
    }

    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
        border-left: 4px solid #ff5e97 !important;
    }
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"]:hover {
        border-color: #ff5e97 !important;
        box-shadow: 0 12px 35px 0 rgba(255, 94, 151, 0.15) !important;
    }

    /* Target specific components of stMetric label/value */
    [data-testid="stMetricLabel"] > div {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #8b9bb4 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetricValue"] > div {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-top: 0.25rem;
        letter-spacing: -0.02em;
    }
    [data-testid="stMetricDelta"] > div {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    /* Green/Red Glowing Indicators for delta/badge updates */
    .badge-glow-green {
        background-color: rgba(0, 242, 254, 0.08) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        color: #00f2fe !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.25rem !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.15) !important;
    }
    .badge-glow-red {
        background-color: rgba(255, 94, 151, 0.08) !important;
        border: 1px solid rgba(255, 94, 151, 0.3) !important;
        color: #ff5e97 !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.25rem !important;
        box-shadow: 0 0 10px rgba(255, 94, 151, 0.15) !important;
    }

    /* Style the file uploader wrapper */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px dashed rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Style inputs, select boxes and multiselects */
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        color: #f0f3f8 !important;
    }
    div[data-baseweb="select"] {
        border-radius: 8px !important;
    }
    
    /* Multiselect chips (Blue pill theme) */
    span[role="button"] {
        background-color: rgba(77, 163, 255, 0.12) !important;
        border: 1px solid rgba(77, 163, 255, 0.2) !important;
        color: #4da3ff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    /* Custom Budget Warning Alert Box (Sleek red glow) */
    div.budget-alert {
        background: rgba(255, 94, 151, 0.03) !important;
        border: 1px solid rgba(255, 94, 151, 0.12) !important;
        border-left: 5px solid #ff5e97 !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(255, 94, 151, 0.04) !important;
        color: #ffb3c6 !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }

    /* Premium styled buttons */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #4da3ff 0%, #a25eff 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(162, 94, 255, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100%;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(162, 94, 255, 0.3) !important;
        background: linear-gradient(135deg, #5fb2ff 0%, #b273ff 100%) !important;
    }
    div[data-testid="stButton"] button:active {
        transform: translateY(0) !important;
    }

    /* Style the sidebar navigation radio selectors as navigation items */
    div[role="radiogroup"] {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        padding: 0.6rem !important;
        gap: 0.5rem !important;
    }
    div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.8rem !important;
        margin-bottom: 0.2rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-color: rgba(77, 163, 255, 0.15) !important;
    }
    div[role="radiogroup"] input[type="radio"] {
        accent-color: #4da3ff !important;
    }

    /* Style Date Picker, Slider, and Number Inputs */
    [data-testid="stSlider"] div[role="slider"] {
        background-color: #4da3ff !important;
        box-shadow: 0 0 10px rgba(77, 163, 255, 0.4) !important;
    }
    [data-testid="stSlider"] div[data-testid="stSliderTrack"] > div {
        background: linear-gradient(90deg, #4da3ff, #a25eff) !important;
    }
    [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
        background-color: rgba(13, 14, 28, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 8px !important;
        color: #f0f3f8 !important;
        padding: 0.4rem 0.6rem !important;
    }
    [data-testid="stNumberInput"] input:focus, [data-testid="stTextInput"] input:focus, [data-testid="stDateInput"] input:focus {
        border-color: #4da3ff !important;
        box-shadow: 0 0 8px rgba(77, 163, 255, 0.2) !important;
    }

    /* Tab Switcher Styling (Clean pill/line themes) */
    div[data-baseweb="tab-list"] {
        background-color: rgba(13, 14, 28, 0.3) !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.03) !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
        gap: 1rem !important;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        color: #8b9bb4 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
    }
    button[aria-selected="true"] {
        color: #4da3ff !important;
        border-bottom: 2px solid #4da3ff !important;
    }

    /* Notification Alerts Styling */
    div[data-testid="stNotification"] {
        background-color: rgba(13, 14, 28, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }

    /* Style the Dataframe view */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
    }

    /* Chat Messages Glassmorphic Design */
    [data-testid="stChatMessage"] {
        background-color: rgba(13, 14, 28, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(8px) !important;
    }
    [data-testid="stChatMessageContent"] {
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: rgba(13, 14, 28, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #4da3ff !important;
        box-shadow: 0 0 10px rgba(77, 163, 255, 0.25) !important;
    }

    /* Style divider lines */
    hr {
        border-color: rgba(255, 255, 255, 0.04) !important;
        margin: 2rem 0 !important;
    }
</style>
"""
