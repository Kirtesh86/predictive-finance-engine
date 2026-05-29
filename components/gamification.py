import streamlit as st
import pandas as pd
from datetime import datetime

def render_rpg_panel(filtered_df: pd.DataFrame) -> None:
    """
    Renders an interactive RPG-style savings progression panel on the dashboard.
    Calculates total monthly budget exhaustion, assigns a gaming rank/level,
    and displays unlocked financial achievements (badges).

    Parameters:
        filtered_df (pd.DataFrame): The filtered transaction database slice.
    """
    budgets = st.session_state.get('budgets', {})
    total_budget = sum(budgets.values())
    
    # Render fallback if budgets are not configured yet
    if total_budget <= 0:
        with st.container(border=True):
            st.markdown("<h3>🏆 Financial RPG Level</h3>", unsafe_allow_html=True)
            st.info("🎯 **Unlock RPG Savings Mode**: Set monthly budget ceilings on the **Settings** page to level up your stats and unlock achievements!")
        return

    # Determine latest month in data
    latest_date = filtered_df['Date'].max()
    current_month = latest_date.month
    current_year = latest_date.year
    
    # Calculate spend in the current month across budgeted categories
    monthly_df = filtered_df[
        (filtered_df['Category'].isin(budgets.keys())) &
        (filtered_df['Date'].dt.month == current_month) &
        (filtered_df['Date'].dt.year == current_year)
    ]
    current_month_spend = float(monthly_df['Amount'].sum())
    
    # Calculate exhaustion metrics
    exhaustion_pct = (current_month_spend / total_budget * 100) if total_budget > 0 else 0.0
    exhaustion_pct = min(100.0, max(0.0, exhaustion_pct))
    
    # Determine RPG level, class rank and styling
    if exhaustion_pct <= 50.0:
        level = 5
        rank_name = "Legendary Grandmaster (Saver Class) 👑"
        color = "#00f2fe"
        flavor_text = "Flawless financial discipline! You have complete command over your capital."
    elif exhaustion_pct <= 75.0:
        level = 3
        rank_name = "Financial Sentinel ⚔️"
        color = "#4da3ff"
        flavor_text = "Vigilant and secure. Your savings shield is strong and holding."
    elif exhaustion_pct <= 100.0:
        level = 1
        rank_name = "Budget Warrior 🛡️"
        color = "#ffd166"
        flavor_text = "Fighting the creep! You are within limits but nearing your thresholds."
    else:
        level = 0
        rank_name = "Debt Barbarian ⚠️"
        color = "#ff5e97"
        flavor_text = "Over-budget rage! Your boundaries have collapsed. Re-group and cut costs."

    # ---------------------------------------------------------
    # Render RPG Card Block
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"<h3>🏆 Financial RPG Rank</h3>", unsafe_allow_html=True)
        
        col_avatar, col_stats = st.columns([1, 4])
        
        with col_avatar:
            # RPG Level Shield badge visual
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem; border: 2px solid {color}; border-radius: 50%; width: 85px; height: 85px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 15px {color}30;">
                    <span style="font-size: 0.7rem; font-weight: 800; color: #8b9bb4; text-transform: uppercase;">LEVEL</span>
                    <span style="font-size: 2rem; font-weight: 800; color: {color}; line-height: 1;">{level}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col_stats:
            st.markdown(f"##### **{rank_name}**")
            st.markdown(f"<small style='color: #8b9bb4;'>*{flavor_text}*</small>", unsafe_allow_html=True)
            
            # Exhaustion Progress Bar
            progress_val = min(1.0, current_month_spend / total_budget)
            st.progress(progress_val)
            st.markdown(
                f"<div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #8b9bb4;'>"
                f"<span>Spent: <b>${current_month_spend:,.2f}</b></span>"
                f"<span>Exhaustion: <b>{exhaustion_pct:.1f}%</b></span>"
                f"<span>Limit: <b>${total_budget:,.2f}</b></span>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 1.25rem 0 !important;'>", unsafe_allow_html=True)
        
        # ---------------------------------------------------------
        # Badge Achievements Checking
        # ---------------------------------------------------------
        st.markdown("##### 🎖️ Unlocked Badges")
        
        # Badge 1: Cafe Disciplined (Coffee spend under $45)
        coffee_df = monthly_df[monthly_df['Description'].str.contains("coffee|starbucks|owl|cafe", case=False, na=False)]
        coffee_spend = coffee_df['Amount'].sum()
        badge_coffee_unlocked = coffee_spend < 45.0
        
        # Badge 2: Rent Sentry (Rent budget active and fully paid)
        rent_spend = monthly_df[monthly_df['Category'] == 'Rent']['Amount'].sum()
        badge_rent_unlocked = rent_spend > 0 and rent_spend <= budgets.get('Rent', 0.0)
        
        # Badge 3: Eco Saver (Utilities under limit)
        utilities_spend = monthly_df[monthly_df['Category'] == 'Utilities']['Amount'].sum()
        badge_utils_unlocked = utilities_spend > 0 and utilities_spend <= budgets.get('Utilities', 0.0)
        
        # Badge 4: Leisure Warden (Entertainment under limit)
        ent_spend = monthly_df[monthly_df['Category'] == 'Entertainment']['Amount'].sum()
        badge_ent_unlocked = ent_spend > 0 and ent_spend <= budgets.get('Entertainment', 0.0)

        # Style sheet override for dynamic badge statuses
        badge_css = """
        <style>
            .rpg-badge {
                padding: 0.75rem !important;
                border-radius: 12px !important;
                text-align: center !important;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                border: 1px solid;
            }
            .rpg-badge-unlocked {
                background: rgba(0, 242, 254, 0.04) !important;
                border-color: rgba(0, 242, 254, 0.25) !important;
                color: #00f2fe !important;
                box-shadow: 0 4px 15px rgba(0, 242, 254, 0.08);
            }
            .rpg-badge-locked {
                background: rgba(255, 255, 255, 0.01) !important;
                border-color: rgba(255, 255, 255, 0.04) !important;
                color: #515e72 !important;
                opacity: 0.45;
                filter: grayscale(100%);
            }
            .rpg-badge-title {
                font-weight: 700;
                font-size: 0.8rem;
                margin-top: 0.35rem;
            }
            .rpg-badge-desc {
                font-size: 0.65rem;
                line-height: 1.2;
            }
        </style>
        """
        st.markdown(badge_css, unsafe_allow_html=True)
        
        # Render Badges in Grid
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        
        # Badge 1
        with col_b1:
            cls = "rpg-badge-unlocked" if badge_coffee_unlocked else "rpg-badge-locked"
            emoji = "☕" if badge_coffee_unlocked else "🔒"
            st.markdown(
                f"""
                <div class="rpg-badge {cls}">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div class="rpg-badge-title">Cafe Sentry</div>
                    <div class="rpg-badge-desc">Coffee spent < $45</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Badge 2
        with col_b2:
            cls = "rpg-badge-unlocked" if badge_rent_unlocked else "rpg-badge-locked"
            emoji = "🛡️" if badge_rent_unlocked else "🔒"
            st.markdown(
                f"""
                <div class="rpg-badge {cls}">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div class="rpg-badge-title">Rent Shield</div>
                    <div class="rpg-badge-desc">Rent under limit</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Badge 3
        with col_b3:
            cls = "rpg-badge-unlocked" if badge_utils_unlocked else "rpg-badge-locked"
            emoji = "⚡" if badge_utils_unlocked else "🔒"
            st.markdown(
                f"""
                <div class="rpg-badge {cls}">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div class="rpg-badge-title">Eco-Guardian</div>
                    <div class="rpg-badge-desc">Utilities in check</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Badge 4
        with col_b4:
            cls = "rpg-badge-unlocked" if badge_ent_unlocked else "rpg-badge-locked"
            emoji = "🎪" if badge_ent_unlocked else "🔒"
            st.markdown(
                f"""
                <div class="rpg-badge {cls}">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div class="rpg-badge-title">Leisure Warden</div>
                    <div class="rpg-badge-desc">Fun spent in check</div>
                </div>
                """,
                unsafe_allow_html=True
            )
