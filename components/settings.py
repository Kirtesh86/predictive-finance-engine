import streamlit as st
import pandas as pd
import numpy as np
import sys
import io
from datetime import datetime
from database import add_transaction
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(df: pd.DataFrame, monthly_average: float, predicted_outflow: float, forecast_horizon: int) -> bytes:
    """
    Constructs a beautifully formatted PDF financial statement using ReportLab.
    """
    buffer = io.BytesIO()
    # Letter size page with 0.5 inch (36 points) margins
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Typography and Branded Hues
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#00f2fe'), # Premium Cyan
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#a25eff'), # Electric Purple
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4
    )
    
    # Document Header
    story.append(Paragraph("🔮 PREDICTIVE FINANCE ENGINE", title_style))
    story.append(Paragraph("<b>Account Holder Statement:</b> Financial Summary Report", body_style))
    story.append(Paragraph(f"<b>Report Run Date:</b> {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", body_style))
    story.append(Spacer(1, 15))
    
    # Summary Performance Grid Table
    total_spent = df['Amount'].sum() if not df.empty else 0.0
    summary_data = [
        ["Total Historical Outflow", "Monthly Average Outflow", f"Predicted Outflow ({forecast_horizon}d)"],
        [f"${total_spent:,.2f}", f"${monthly_average:,.2f}", f"${predicted_outflow:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0a0b14')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 13),
        ('TOPPADDING', (0,1), (-1,-1), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Category Summaries Table
    story.append(Paragraph("Category Spending Breakdown", h2_style))
    cat_df = df.groupby('Category')['Amount'].sum().reset_index()
    cat_data = [["Category Group", "Aggregated Outflow", "Outflow Share (%)"]]
    
    for _, row in cat_df.iterrows():
        pct = (row['Amount'] / total_spent * 100) if total_spent > 0 else 0.0
        cat_data.append([
            str(row['Category']),
            f"${row['Amount']:,.2f}",
            f"{pct:.1f}%"
        ])
        
    cat_table = Table(cat_data, colWidths=[180, 180, 180])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 20))
    
    # Recent Transactions Logs
    story.append(Paragraph("Historical Transaction log sheet (Last 30 Entries)", h2_style))
    tx_data = [["Date", "Category", "Amount", "Description Memo"]]
    
    sorted_df = df.sort_values(by="Date", ascending=False).head(30)
    for _, row in sorted_df.iterrows():
        tx_data.append([
            row['Date'].strftime('%Y-%m-%d'),
            str(row['Category']),
            f"${row['Amount']:,.2f}",
            str(row['Description'])
        ])
        
    tx_table = Table(tx_data, colWidths=[90, 100, 90, 260])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(tx_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_settings(filtered_df: pd.DataFrame, db_session: Session) -> None:
    """
    Renders the Settings page, allowing users to configure forecasting algorithms,
    set category budget limits, input Gemini API keys, manually insert transaction entries 
    into the SQLite DB, export data slices, and review system info.
    """
    st.markdown("Tune machine learning estimators, adjust category budget ceilings, and manage database entries.")
    
    col_set1, col_set2 = st.columns([1, 1])
    
    # ---------------------------------------------------------
    # Column 1: Forecasting Settings, Gemini API Config & System Info
    # ---------------------------------------------------------
    with col_set1:
        with st.container(border=True):
            st.markdown("<h4>⚙️ Model Configuration</h4>", unsafe_allow_html=True)
            
            st.selectbox(
                "Model Algorithm Type",
                options=["Random Forest Regressor", "Linear Regression"],
                key="ml_model_type",
                help="Choose between Random Forest (captures seasonality) and Linear Regression (projects macro trend directions)."
            )
            
            st.slider(
                "Prediction Horizon (Days)",
                min_value=15,
                max_value=90,
                step=5,
                key="forecast_horizon",
                help="Configure how many days into the future the predictive engine should calculate spending projections."
            )
            
            if st.session_state.ml_model_type == "Random Forest Regressor":
                st.slider(
                    "Random Forest Estimators (Trees)",
                    min_value=50,
                    max_value=200,
                    step=10,
                    key="rf_estimators",
                    help="Determine the number of decision trees in the ensemble."
                )
                
        with st.container(border=True):
            st.markdown("<h4>🔮 AI Agent Configuration</h4>", unsafe_allow_html=True)
            st.markdown("Entering a Gemini API key unlocks cognitive text analysis and insights on the **AI Financial Agent** page.")
            
            st.text_input(
                "Google Gemini API Key",
                type="password",
                key="gemini_api_key",
                placeholder="AI Studio API Key (AI_KEY_...)",
                help="Input your Google Gemini API Key. Kept secure within your active local session state."
            )
            
        with st.container(border=True):
            st.markdown("<h4>💾 Data Export & Info</h4>", unsafe_allow_html=True)
            st.markdown("Download your current filtered slice of data for local inspection or reporting.")
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                # CSV Exporter
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Filtered CSV",
                    data=csv_data,
                    file_name=f"finance_engine_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_exp2:
                # PDF Exporter
                if not filtered_df.empty:
                    # Run daily forecast for the PDF projection values
                    from ml_pipeline import aggregate_and_forecast
                    _, daily_forecast, _ = aggregate_and_forecast(
                        filtered_df, 
                        interval="Daily",
                        model_type=st.session_state.ml_model_type,
                        estimators=st.session_state.rf_estimators,
                        periods=st.session_state.forecast_horizon
                    )
                    predicted_outflow = daily_forecast['Amount'].sum()
                    monthly_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['Amount'].sum()
                    monthly_average = monthly_data.mean() if not monthly_data.empty else 0.0
                    
                    pdf_bytes = generate_pdf_report(
                        df=filtered_df,
                        monthly_average=monthly_average,
                        predicted_outflow=predicted_outflow,
                        forecast_horizon=st.session_state.forecast_horizon
                    )
                    
                    st.download_button(
                        label="📄 Download PDF Summary",
                        data=pdf_bytes,
                        file_name=f"finance_engine_statement_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.button("📄 PDF Export Unavailable", disabled=True, use_container_width=True)
            
            st.markdown("---")
            st.markdown("##### 💻 Environment Details")
            st.code(
                f"Python: {sys.version.split()[0]}\n"
                f"Pandas: {pd.__version__}\n"
                f"Numpy: {np.__version__}\n"
                f"Scikit-Learn: 1.8.0\n"
                f"SQLAlchemy: 2.0.50"
            )
            
    # ---------------------------------------------------------
    # Column 2: Budget Ceilings & Manual Database Insert Form
    # ---------------------------------------------------------
    with col_set2:
        with st.container(border=True):
            st.markdown("<h4>🎯 Budget Limits Configuration</h4>", unsafe_allow_html=True)
            st.markdown("Set monthly spending thresholds. If ML forecasts project a breach within 15 days, a dashboard alert triggers.")
            
            # Initialize budgets dict in session state if not exists
            if 'budgets' not in st.session_state:
                st.session_state.budgets = {"Food": 300.0, "Rent": 1200.0, "Utilities": 200.0, "Entertainment": 150.0}
                
            new_budgets = {}
            for cat in ["Food", "Rent", "Utilities", "Entertainment"]:
                current_limit = st.session_state.budgets.get(cat, 0.0)
                new_budgets[cat] = st.number_input(
                    f"{cat} Limit ($)",
                    min_value=0.0,
                    max_value=15000.0,
                    value=float(current_limit),
                    step=25.0,
                    help=f"Set spending ceiling for the {cat} category. Set to 0 to disable alerts."
                )
            
            # Save updates to session state
            st.session_state.budgets = new_budgets
            
        with st.container(border=True):
            st.markdown("<h4>➕ Insert Transaction</h4>", unsafe_allow_html=True)
            st.markdown("Directly append a transaction entry into the SQLite backend database tables.")
            
            # Insert Transaction Form layout
            with st.form("insert_tx_form", clear_on_submit=True):
                tx_date = st.date_input("Transaction Date", value=datetime.today().date())
                
                tx_category = st.selectbox(
                    "Category",
                    options=["Food", "Rent", "Utilities", "Entertainment", "Other"]
                )
                
                tx_amount = st.number_input(
                    "Amount ($)", 
                    min_value=0.01, 
                    max_value=50000.00, 
                    step=5.00, 
                    format="%.2f"
                )
                
                tx_account = st.selectbox(
                    "Account Type",
                    options=["Credit Card", "Checking Account", "Savings Account", "Cash"]
                )
                
                tx_desc = st.text_input(
                    "Description / Memo",
                    placeholder="e.g. Owl Night Cafe (Nandanvan), Whole Foods groceries"
                )
                
                submit_button = st.form_submit_button(label="Add Transaction")
                
                if submit_button:
                    try:
                        add_transaction(
                            session=db_session,
                            transaction_date=tx_date,
                            category=tx_category,
                            amount=float(tx_amount),
                            account_type=tx_account,
                            description=tx_desc
                        )
                        st.success(f"Success: Added {tx_category} transaction of ${tx_amount:.2f}!")
                        # Trigger app rerun to pull newly added transaction on redirect
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to insert transaction: {e}")
