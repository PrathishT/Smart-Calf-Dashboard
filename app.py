import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import re
import math
import random

# ==============================================================================
# 1. STREAMLIT APP CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SMART CALF SENSE - IoT Monitoring",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. DESIGN SYSTEM & CUSTOM CSS (DYNAMIC DARK & LIGHT THEMES)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3.2rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        max-width: 100%;
    }

    /* -------------------------------------------------------------------------
       BASE THEME CONTAINERS
       ------------------------------------------------------------------------- */
    [data-theme="light"] .stApp,
    [data-base-theme="light"] .stApp,
    .stApp.light-theme {
        background-color: #f8fafc;
        color: #0f172a;
    }

    [data-theme="dark"] .stApp,
    [data-base-theme="dark"] .stApp,
    .stApp.dark-theme {
        background-color: #0b0f19;
        color: #f8fafc;
    }

    /* -------------------------------------------------------------------------
       DASHBOARD HEADER
       ------------------------------------------------------------------------- */
    .dashboard-header {
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: background 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }

    /* Dark Header (Default) */
    .dashboard-header,
    .dashboard-header.dark-theme,
    [data-theme="dark"] .dashboard-header,
    [data-base-theme="dark"] .dashboard-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.4), 0 0 20px rgba(14, 165, 233, 0.12);
    }

    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3.5px;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c9ff 100%);
    }

    /* Light Header */
    .dashboard-header.light-theme,
    [data-theme="light"] .dashboard-header,
    [data-base-theme="light"] .dashboard-header {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    }

    .dashboard-header.light-theme::before,
    [data-theme="light"] .dashboard-header::before,
    [data-base-theme="light"] .dashboard-header::before {
        display: none !important;
    }

    /* Title Styling */
    .title-text {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Dark Title (Gradient) */
    .title-text,
    .title-text.dark-theme,
    [data-theme="dark"] .title-text,
    [data-base-theme="dark"] .title-text {
        background: linear-gradient(135deg, #ffffff 40%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Light Title (Solid Navy/Blue) */
    .title-text.light-theme,
    [data-theme="light"] .title-text,
    [data-base-theme="light"] .title-text {
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: #0284c7 !important;
        color: #0284c7 !important;
    }

    /* Subtitle & Backend Meta */
    .subtitle-text {
        font-size: 0.96rem;
        font-weight: 400;
        margin-top: 5px;
        margin-bottom: 0;
        color: #94a3b8;
    }

    .subtitle-text.light-theme,
    [data-theme="light"] .subtitle-text,
    [data-base-theme="light"] .subtitle-text {
        color: #64748b !important;
    }

    .backend-meta-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94a3b8;
    }

    .backend-meta-text.light-theme,
    [data-theme="light"] .backend-meta-text,
    [data-base-theme="light"] .backend-meta-text {
        color: #64748b !important;
    }

    /* -------------------------------------------------------------------------
       CONNECTION STATUS BADGES (HEADER PILL)
       ------------------------------------------------------------------------- */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        transition: all 0.2s ease;
    }

    /* Dark Status Badges */
    .status-connected {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1.5px solid rgba(16, 185, 129, 0.6);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
    }

    .status-disconnected {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1.5px solid rgba(239, 68, 68, 0.6);
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.25);
    }

    /* Light Status Badges */
    [data-theme="light"] .status-connected,
    [data-base-theme="light"] .status-connected,
    .light-theme .status-connected {
        background: #ecfdf5 !important;
        color: #10b981 !important;
        border: 1.5px solid #a7f3d0 !important;
        box-shadow: none !important;
    }

    [data-theme="light"] .status-disconnected,
    [data-base-theme="light"] .status-disconnected,
    .light-theme .status-disconnected {
        background: #fee2e2 !important;
        color: #ef4444 !important;
        border: 1.5px solid #fca5a5 !important;
        box-shadow: none !important;
    }

    .pulsing-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: currentColor;
        box-shadow: 0 0 10px currentColor;
        animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.35); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }

    /* -------------------------------------------------------------------------
       TOP SUMMARY CARDS (FOUR METRIC CARDS)
       ------------------------------------------------------------------------- */
    .summary-card {
        border-radius: 16px;
        padding: 20px 22px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Dark Mode Summary Cards (Default) */
    .summary-card,
    .summary-card.dark-theme,
    [data-theme="dark"] .summary-card,
    [data-base-theme="dark"] .summary-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.28);
    }

    .summary-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
    }

    .card-connection {
        border: 1.5px solid rgba(56, 189, 248, 0.4);
        background: linear-gradient(145deg, rgba(14, 116, 144, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%);
    }

    .card-battery {
        border: 1.5px solid rgba(16, 185, 129, 0.4);
        background: linear-gradient(145deg, rgba(6, 78, 59, 0.25) 0%, rgba(15, 23, 42, 0.92) 100%);
    }

    .card-total-standing {
        border: 1.5px solid rgba(168, 85, 247, 0.4);
        background: linear-gradient(145deg, rgba(109, 40, 217, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%);
    }

    .card-current-session {
        border: 1.5px solid rgba(59, 130, 246, 0.4);
        background: linear-gradient(145deg, rgba(29, 78, 216, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%);
    }

    /* Light Mode Summary Cards */
    .summary-card.light-theme,
    [data-theme="light"] .summary-card,
    [data-base-theme="light"] .summary-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    }

    .summary-card.light-theme:hover,
    [data-theme="light"] .summary-card:hover,
    [data-base-theme="light"] .summary-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08) !important;
        border-color: #cbd5e1 !important;
    }

    .card-header-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    [data-theme="light"] .card-header-label,
    [data-base-theme="light"] .card-header-label,
    .light-theme .card-header-label {
        color: #64748b !important;
    }

    .card-main-val {
        font-size: 2.15rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    .card-subtitle {
        font-size: 0.8rem;
        color: #cbd5e1;
        font-weight: 500;
        line-height: 1.3;
    }

    [data-theme="light"] .card-subtitle,
    [data-base-theme="light"] .card-subtitle,
    .light-theme .card-subtitle {
        color: #334155 !important;
        font-weight: 600 !important;
    }

    .card-footnote {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 3px;
        font-style: italic;
    }

    [data-theme="light"] .card-footnote,
    [data-base-theme="light"] .card-footnote,
    .light-theme .card-footnote {
        color: #94a3b8 !important;
    }

    /* -------------------------------------------------------------------------
       SESSION DETAILS BOX (SIX METRICS BAR)
       ------------------------------------------------------------------------- */
    .session-details-box {
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 14px;
        transition: all 0.25s ease;
    }

    /* Dark Session Details Box */
    .session-details-box,
    .session-details-box.dark-theme,
    [data-theme="dark"] .session-details-box,
    [data-base-theme="dark"] .session-details-box {
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }

    /* Light Session Details Box */
    .session-details-box.light-theme,
    [data-theme="light"] .session-details-box,
    [data-base-theme="light"] .session-details-box {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    }

    .session-item-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.8px;
    }

    [data-theme="light"] .session-item-label,
    [data-base-theme="light"] .session-item-label,
    .light-theme .session-item-label {
        color: #64748b !important;
    }

    .session-item-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 700;
    }

    .session-item-val.val-primary {
        color: #f8fafc;
    }

    [data-theme="light"] .session-item-val.val-primary,
    [data-base-theme="light"] .session-item-val.val-primary,
    .light-theme .session-item-val.val-primary {
        color: #0f172a !important;
    }

    .session-item-val.val-blue {
        color: #38bdf8;
    }

    [data-theme="light"] .session-item-val.val-blue,
    [data-base-theme="light"] .session-item-val.val-blue,
    .light-theme .session-item-val.val-blue {
        color: #0284c7 !important;
    }

    .session-item-val.val-amber {
        color: #fbbf24;
    }

    [data-theme="light"] .session-item-val.val-amber,
    [data-base-theme="light"] .session-item-val.val-amber,
    .light-theme .session-item-val.val-amber {
        color: #d97706 !important;
    }

    /* -------------------------------------------------------------------------
       CONNECTION ALERT BANNER (DISCONNECTED STATE)
       ------------------------------------------------------------------------- */
    .connection-alert-box {
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        transition: all 0.25s ease;
    }

    .connection-alert-box.dark-theme,
    [data-theme="dark"] .connection-alert-box,
    [data-base-theme="dark"] .connection-alert-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1.5px solid rgba(239, 68, 68, 0.45);
    }

    .connection-alert-box.light-theme,
    [data-theme="light"] .connection-alert-box,
    [data-base-theme="light"] .connection-alert-box {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.05) !important;
    }

    .connection-alert-title {
        font-weight: 800;
        color: #fca5a5;
        font-size: 0.95rem;
    }

    [data-theme="light"] .connection-alert-title,
    [data-base-theme="light"] .connection-alert-title,
    .light-theme .connection-alert-title {
        color: #dc2626 !important;
    }

    .connection-alert-desc {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.4;
    }

    [data-theme="light"] .connection-alert-desc,
    [data-base-theme="light"] .connection-alert-desc,
    .light-theme .connection-alert-desc {
        color: #475569 !important;
    }

    /* -------------------------------------------------------------------------
       SECTION HEADERS
       ------------------------------------------------------------------------- */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 24px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.2px;
    }

    .section-title.light-theme,
    [data-theme="light"] .section-title,
    [data-base-theme="light"] .section-title {
        color: #0f172a !important;
    }

    /* -------------------------------------------------------------------------
       ACTIVITY CARD & ALERT BANNER
       ------------------------------------------------------------------------- */
    .activity-card {
        border-radius: 14px;
        padding: 18px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.25s ease;
    }

    .activity-card.dark-theme,
    [data-theme="dark"] .activity-card,
    [data-base-theme="dark"] .activity-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
    }

    .activity-card.light-theme,
    [data-theme="light"] .activity-card,
    [data-base-theme="light"] .activity-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    }

    .activity-card-label {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.8px;
    }

    [data-theme="light"] .activity-card-label,
    [data-base-theme="light"] .activity-card-label,
    .light-theme .activity-card-label {
        color: #64748b !important;
    }

    .activity-card-desc {
        font-size: 0.78rem;
        color: #94a3b8;
    }

    [data-theme="light"] .activity-card-desc,
    [data-base-theme="light"] .activity-card-desc,
    .light-theme .activity-card-desc {
        color: #64748b !important;
    }

    /* Activity Badges */
    .activity-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 1.25rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }

    /* Dark Activity Badges */
    .activity-standing {
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1.5px solid rgba(59, 130, 246, 0.55);
    }

    .activity-sitting {
        background: rgba(139, 92, 246, 0.2);
        color: #c084fc;
        border: 1.5px solid rgba(139, 92, 246, 0.55);
    }

    .activity-walking {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1.5px solid rgba(16, 185, 129, 0.55);
    }

    .activity-moving {
        background: rgba(6, 182, 212, 0.2);
        color: #22d3ee;
        border: 1.5px solid rgba(6, 182, 212, 0.55);
    }

    .activity-unknown {
        background: rgba(148, 163, 184, 0.2);
        color: #cbd5e1;
        border: 1.5px solid rgba(148, 163, 184, 0.4);
    }

    /* Light Activity Badges */
    [data-theme="light"] .activity-moving,
    [data-base-theme="light"] .activity-moving,
    .light-theme .activity-moving {
        background: #e0f2fe !important;
        color: #0284c7 !important;
        border: 1.5px solid #7dd3fc !important;
    }

    [data-theme="light"] .activity-standing,
    [data-base-theme="light"] .activity-standing,
    .light-theme .activity-standing {
        background: #eff6ff !important;
        color: #2563eb !important;
        border: 1.5px solid #93c5fd !important;
    }

    [data-theme="light"] .activity-sitting,
    [data-base-theme="light"] .activity-sitting,
    .light-theme .activity-sitting {
        background: #faf5ff !important;
        color: #7c3aed !important;
        border: 1.5px solid #d8b4fe !important;
    }

    [data-theme="light"] .activity-walking,
    [data-base-theme="light"] .activity-walking,
    .light-theme .activity-walking {
        background: #f0fdf4 !important;
        color: #16a34a !important;
        border: 1.5px solid #86efac !important;
    }

    [data-theme="light"] .activity-unknown,
    [data-base-theme="light"] .activity-unknown,
    .light-theme .activity-unknown {
        background: #f8fafc !important;
        color: #64748b !important;
        border: 1.5px solid #cbd5e1 !important;
    }

    /* Alert Banners (Right Side) */
    .alert-banner {
        border-radius: 14px;
        padding: 16px 22px;
        display: flex;
        align-items: center;
        gap: 18px;
        transition: all 0.25s ease;
    }

    /* Dark Alert Banners */
    .alert-normal {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.45) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1.5px solid #10b981;
        color: #34d399;
    }

    .alert-warning {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.45) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1.5px solid #f59e0b;
        color: #fbbf24;
    }

    .alert-alert {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.6) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1.5px solid #ef4444;
        color: #f87171;
        animation: alert-pulse 1.8s infinite;
    }

    @keyframes alert-pulse {
        0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.6); }
        100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
    }

    .alert-banner-title {
        font-weight: 800;
        font-size: 1.15rem;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .alert-banner-desc {
        font-size: 0.86rem;
        opacity: 0.92;
        line-height: 1.4;
    }

    /* Light Alert Banners */
    [data-theme="light"] .alert-banner.alert-normal,
    [data-base-theme="light"] .alert-banner.alert-normal,
    .light-theme .alert-banner.alert-normal {
        background: #f0fdf4 !important;
        border: 1.5px solid #86efac !important;
        color: #15803d !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.08) !important;
    }

    [data-theme="light"] .alert-banner.alert-normal .alert-banner-title,
    [data-base-theme="light"] .alert-banner.alert-normal .alert-banner-title,
    .light-theme .alert-banner.alert-normal .alert-banner-title {
        color: #15803d !important;
    }

    [data-theme="light"] .alert-banner.alert-normal .alert-banner-desc,
    [data-base-theme="light"] .alert-banner.alert-normal .alert-banner-desc,
    .light-theme .alert-banner.alert-normal .alert-banner-desc {
        color: #166534 !important;
        opacity: 0.95 !important;
    }

    [data-theme="light"] .alert-banner.alert-warning,
    [data-base-theme="light"] .alert-banner.alert-warning,
    .light-theme .alert-banner.alert-warning {
        background: #fffbeb !important;
        border: 1.5px solid #fcd34d !important;
        color: #b45309 !important;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.08) !important;
    }

    [data-theme="light"] .alert-banner.alert-warning .alert-banner-title,
    [data-base-theme="light"] .alert-banner.alert-warning .alert-banner-title,
    .light-theme .alert-banner.alert-warning .alert-banner-title {
        color: #b45309 !important;
    }

    [data-theme="light"] .alert-banner.alert-warning .alert-banner-desc,
    [data-base-theme="light"] .alert-banner.alert-warning .alert-banner-desc,
    .light-theme .alert-banner.alert-warning .alert-banner-desc {
        color: #92400e !important;
        opacity: 0.95 !important;
    }

    [data-theme="light"] .alert-banner.alert-alert,
    [data-base-theme="light"] .alert-banner.alert-alert,
    .light-theme .alert-banner.alert-alert {
        background: #fef2f2 !important;
        border: 1.5px solid #fca5a5 !important;
        color: #b91c1c !important;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.08) !important;
    }

    [data-theme="light"] .alert-banner.alert-alert .alert-banner-title,
    [data-base-theme="light"] .alert-banner.alert-alert .alert-banner-title,
    .light-theme .alert-banner.alert-alert .alert-banner-title {
        color: #b91c1c !important;
    }

    [data-theme="light"] .alert-banner.alert-alert .alert-banner-desc,
    [data-base-theme="light"] .alert-banner.alert-alert .alert-banner-desc,
    .light-theme .alert-banner.alert-alert .alert-banner-desc {
        color: #991b1b !important;
        opacity: 0.95 !important;
    }

    /* -------------------------------------------------------------------------
       COMPACT SENSOR CARDS (LIVE SENSOR DATA)
       ------------------------------------------------------------------------- */
    .sensor-card {
        border-radius: 12px;
        padding: 14px 16px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    /* Dark Sensor Cards */
    .sensor-card,
    .sensor-card.dark-theme,
    [data-theme="dark"] .sensor-card,
    [data-base-theme="dark"] .sensor-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
    }

    .sensor-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.35);
    }

    .sensor-card-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .sensor-card-val {
        font-size: 1.55rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 2px;
        margin-bottom: 2px;
    }

    .sensor-card-sub {
        font-size: 0.74rem;
        color: #64748b;
    }

    /* Light Sensor Cards */
    .sensor-card.light-theme,
    [data-theme="light"] .sensor-card,
    [data-base-theme="light"] .sensor-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    .sensor-card.light-theme:hover,
    [data-theme="light"] .sensor-card:hover,
    [data-base-theme="light"] .sensor-card:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
    }

    [data-theme="light"] .sensor-card-label,
    [data-base-theme="light"] .sensor-card-label,
    .light-theme .sensor-card-label {
        color: #64748b !important;
    }

    [data-theme="light"] .sensor-card-sub,
    [data-base-theme="light"] .sensor-card-sub,
    .light-theme .sensor-card-sub {
        color: #94a3b8 !important;
    }

    /* -------------------------------------------------------------------------
       SIDEBAR & WIDGET THEME TWEAKS
       ------------------------------------------------------------------------- */
    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.3px;
    }

    [data-theme="light"] .sidebar-brand-title,
    [data-base-theme="light"] .sidebar-brand-title,
    .light-theme .sidebar-brand-title {
        color: #0f172a !important;
    }

    .sidebar-brand-sub {
        font-size: 0.76rem;
        color: #38bdf8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-theme="light"] .sidebar-brand-sub,
    [data-base-theme="light"] .sidebar-brand-sub,
    .light-theme .sidebar-brand-sub {
        color: #0284c7 !important;
    }

    /* Expanders & Tabs in Light Theme */
    [data-theme="light"] [data-testid="stExpander"],
    [data-base-theme="light"] [data-testid="stExpander"],
    .light-theme [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. HELPER UTILITIES: FORMATTERS & PARSERS
# ==============================================================================

def format_hms(seconds):
    """Formats seconds into strict HH:MM:SS format."""
    seconds = max(0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def format_friendly_duration(seconds):
    """
    Formats seconds into clean summary string:
      - '2h 34m' if >= 1 hour
      - '18m 42s' or '10 min' if < 1 hour
    """
    seconds = max(0, float(seconds))
    if seconds >= 3600:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h}h {m}m"
    elif seconds >= 60:
        m = int(seconds // 60)
        s = int(seconds % 60)
        if s > 0:
            return f"{m}m {s:02d}s"
        return f"{m} min"
    else:
        return f"{int(seconds)}s"

def convert_to_ist(timestamp):
    """Convert ThingSpeak UTC timestamp to India Standard Time."""
    if timestamp is None or pd.isna(timestamp):
        return None

    dt = pd.to_datetime(timestamp, utc=True)
    return dt.tz_convert("Asia/Kolkata")

def extract_numeric(val, default=0.0):
    if val is None or pd.isna(val):
        return default
    if isinstance(val, (int, float)):
        return float(val)
    match = re.search(r"[-+]?\d*\.?\d+", str(val))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return default
    return default

def normalize_activity(raw_val):
    if raw_val is None or pd.isna(raw_val):
        return "UNKNOWN"
    val_str = str(raw_val).strip().upper()
    code_map = {"0": "SITTING", "1": "STANDING", "2": "MOVING", "3": "UNCERTAIN"}
    if val_str in code_map:
        return code_map[val_str]
    for known in ["SITTING", "STANDING", "MOVING", "UNCERTAIN", "UNKNOWN"]:
        if known in val_str:
            return known
    return val_str if val_str else "UNKNOWN"

def normalize_alert(raw_val):
    if raw_val is None or pd.isna(raw_val):
        return "NORMAL"
    val_str = str(raw_val).strip().upper()
    code_map = {"0": "NORMAL", "1": "WARNING", "2": "ALERT"}
    if val_str in code_map:
        return code_map[val_str]
    for known in ["ALERT", "WARNING", "NORMAL"]:
        if known in val_str:
            return known
    return val_str if val_str else "NORMAL"

def get_activity_badge_class(activity):
    act = activity.upper()
    if "STAND" in act: return "activity-standing"
    elif "SIT" in act: return "activity-sitting"
    elif "WALK" in act: return "activity-walking"
    elif "MOV" in act: return "activity-moving"
    else: return "activity-unknown"

def get_activity_icon(activity):
    act = activity.upper()
    if "STAND" in act: return "🧍"
    elif "SIT" in act: return "🪑"
    elif "WALK" in act: return "🚶"
    elif "MOV" in act: return "🏃"
    else: return "❓"

# ==============================================================================
# 4. ESTIMATED BATTERY CONSUMPTION MODEL
# ==============================================================================

def compute_session_battery_trace(session_feeds, capacity_mah=2000, accel_factor=1.0):
    """
    Estimates battery percentage decreasing during the CURRENT SESSION.
    
    CRITICAL HARDWARE CONTEXT:
      - There is NO battery voltage sensor or fuel gauge IC on the hardware.
      - DO NOT claim this is measured. It is purely an estimate.
      - Core Assumption: Smart Calf Sense is charged before/after every use.
      - Therefore, every NEW session begins at 100%.
      - Previous session's battery percentage MUST NOT carry over.
      - Disconnection ends the battery session (freezes).
      - Reconnection starts a NEW session with Estimated Battery = 100%.

    Power Consumption Model Assumptions:
      - ESP32 active + Wi-Fi bursts (every 15s): ~135 mA average
      - MPU6050 6-DoF sensor: ~3.8 mA
      - FSR402 voltage divider: ~0.5 mA
      - Base active consumption: I_base = 140 mA
      - Vibration motor active (during WARNING/ALERT prompts): +80 mA (~220 mA total)
      - Consumed mAh = (Current_mA * Time_hours)
      - Remaining % = max(0, min(100, (Capacity - Consumed) / Capacity * 100))
    """
    if not session_feeds:
        return 100.0, 0.0, []

    base_ma = 140.0 * accel_factor
    vib_ma = 80.0 * accel_factor

    battery_points = []
    cumulative_consumed_mah = 0.0

    sorted_feeds = sorted(session_feeds, key=lambda x: x["created_at"])

    for i, feed in enumerate(sorted_feeds):
        if i == 0:
            dt_sec = 15.0  # baseline packet duration
        else:
            prev_t = sorted_feeds[i - 1]["created_at"]
            curr_t = feed["created_at"]
            dt_sec = min((curr_t - prev_t).total_seconds(), 45.0)

        dt_hours = dt_sec / 3600.0
        alert_str = str(feed.get("Alert", "")).upper()
        is_vib = ("ALERT" in alert_str) or ("WARN" in alert_str)
        current_draw = base_ma + (vib_ma if is_vib else 0.0)

        step_consumed = current_draw * dt_hours
        cumulative_consumed_mah += step_consumed

        rem_mah = max(0.0, capacity_mah - cumulative_consumed_mah)
        pct = max(0.0, min(100.0, (rem_mah / capacity_mah) * 100.0))

        battery_points.append({
            "created_at": feed["created_at"],
            "estimated_battery_pct": round(pct, 1),
            "consumed_mah": round(cumulative_consumed_mah, 1),
            "remaining_mah": round(rem_mah, 1)
        })

    final_pct = battery_points[-1]["estimated_battery_pct"]
    final_consumed = battery_points[-1]["consumed_mah"]
    return final_pct, final_consumed, battery_points

def get_battery_status_level(pct):
    """Returns battery level category and color based on Section 11 specifications."""
    if pct > 30.0:
        return "Normal", "#10b981", "🟢"
    elif pct >= 15.0:
        return "Low", "#f59e0b", "🟡"
    elif pct >= 5.0:
        return "Very Low", "#f97316", "🟠"
    else:
        return "Critical", "#ef4444", "🔴"

# ==============================================================================
# 5. SESSION MANAGER (HEARTBEAT & DUAL STANDING TIME ENGINE)
# ==============================================================================

class SessionManager:
    """
    Manages connection state, heartbeat monitoring, dual standing times,
    and session battery tracking.
    """
    def __init__(self, history_file=".streamlit/session_history.json", heartbeat_timeout=45):
        self.history_file = Path(history_file)
        self.heartbeat_timeout = heartbeat_timeout
        self.state = self._load()

    def _load(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "sessions": [],
            "total_standing_seconds": 0.0,
            "last_entry_id": 0
        }

    def _save(self):
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w") as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception:
            pass

    def reset_all(self):
        self.state = {
            "sessions": [],
            "total_standing_seconds": 0.0,
            "last_entry_id": 0
        }
        self._save()

    def process(self, df, is_simulated=False, sim_force_disconnect=False, battery_capacity=2000, accel_factor=1.0):
        if df is None or df.empty:
            return {
                "connection_status": "DISCONNECTED",
                "session_id": 1,
                "session_start": None,
                "last_data_received": None,
                "current_session_seconds": 0.0,
                "total_standing_seconds": 0.0,
                "estimated_battery_pct": 100.0,
                "battery_consumed_mah": 0.0,
                "current_session_battery_trace": [],
                "seconds_since_last": None,
                "sessions_history": []
            }

        sorted_df = df.sort_values(by="created_at").reset_index(drop=True)
        now_utc = datetime.now(timezone.utc)

        # Segment feeds into discrete sessions by detecting gaps > heartbeat_timeout
        detected_sessions = []
        current_sess_feeds = []

        for i in range(len(sorted_df)):
            curr_row = sorted_df.iloc[i]
            curr_time = curr_row["created_at"]

            if not current_sess_feeds:
                current_sess_feeds.append(curr_row)
            else:
                prev_time = current_sess_feeds[-1]["created_at"]
                gap_sec = (curr_time - prev_time).total_seconds()

                if gap_sec > self.heartbeat_timeout:
                    detected_sessions.append(current_sess_feeds)
                    current_sess_feeds = [curr_row]
                else:
                    current_sess_feeds.append(curr_row)

        if current_sess_feeds:
            detected_sessions.append(current_sess_feeds)

        # Compute standing duration for each session
        session_summaries = []
        total_accumulated_seconds = 0.0

        for idx, s_feeds in enumerate(detected_sessions):
            sess_id = idx + 1
            s_df = pd.DataFrame(s_feeds)
            start_t = s_df["created_at"].iloc[0]
            end_t = s_df["created_at"].iloc[-1]

            sess_standing_seconds = 0.0
            for k in range(len(s_df)):
                row_k = s_df.iloc[k]
                act_k = str(row_k.get("Activity", "")).upper()
                if "STAND" in act_k:
                    if k == 0:
                        delta = 15.0
                    else:
                        dt = (row_k["created_at"] - s_df.iloc[k - 1]["created_at"]).total_seconds()
                        delta = min(dt, 30.0) if dt <= self.heartbeat_timeout else 15.0
                    sess_standing_seconds += delta

            session_summaries.append({
                "session_id": sess_id,
                "start_time": start_t,
                "end_time": end_t,
                "standing_seconds": sess_standing_seconds,
                "feed_count": len(s_df),
                "is_active": (idx == len(detected_sessions) - 1),
                "raw_feeds": s_feeds
            })
            total_accumulated_seconds += sess_standing_seconds

        active_session = session_summaries[-1]
        latest_feed = sorted_df.iloc[-1]
        latest_timestamp = latest_feed["created_at"]

        # Calculate time since last packet for heartbeat connection status
        if isinstance(latest_timestamp, pd.Timestamp):
            last_dt = latest_timestamp.to_pydatetime()
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            seconds_since_last = (now_utc - last_dt).total_seconds()
        else:
            seconds_since_last = 0.0

        if sim_force_disconnect:
            is_connected = False
        elif is_simulated:
            is_connected = not sim_force_disconnect
        else:
            is_connected = (seconds_since_last <= self.heartbeat_timeout)

        # Calculate Estimated Battery for the CURRENT SESSION
        active_feeds_list = [row.to_dict() if isinstance(row, pd.Series) else row for row in active_session["raw_feeds"]]
        est_battery_pct, battery_consumed_mah, battery_trace = compute_session_battery_trace(
            active_feeds_list,
            capacity_mah=battery_capacity,
            accel_factor=accel_factor
        )

        # Save to persistent storage
        self.state["sessions"] = session_summaries
        self.state["total_standing_seconds"] = total_accumulated_seconds
        self.state["last_entry_id"] = int(latest_feed.get("entry_id", 0))
        self._save()

        return {
            "connection_status": "CONNECTED" if is_connected else "DISCONNECTED",
            "session_id": active_session["session_id"],
            "session_start": active_session["start_time"],
            "last_data_received": latest_timestamp,
            "current_session_seconds": active_session["standing_seconds"],
            "total_standing_seconds": total_accumulated_seconds,
            "estimated_battery_pct": est_battery_pct,
            "battery_consumed_mah": battery_consumed_mah,
            "current_session_battery_trace": battery_trace,
            "seconds_since_last": seconds_since_last,
            "sessions_history": session_summaries
        }

# ==============================================================================
# 6. SIMULATION DATA GENERATOR (Realistic Multi-Session Telemetry)
# ==============================================================================

def generate_simulation_data(num_points=50):
    """
    Generates realistic multi-session calf telemetry matching the user specification:
      Session 1: 15 min standing (disconnected)
      Session 2: 20 min standing (disconnected)
      Session 3: 10 min standing (currently connected)
      Total Standing = 45 min
      Current Session Standing = 10 min
    """
    now = datetime.now(timezone.utc)
    records = []

    # Session 1: 15 min standing (2 hours ago)
    s1_start = now - timedelta(hours=2)
    for i in range(20):
        t = s1_start + timedelta(seconds=i * 15)
        records.append({
            "created_at": t,
            "entry_id": len(records) + 1,
            "FSR": round(random.gauss(245, 18), 1),
            "Accel_X": round(random.gauss(0.12, 0.04), 3),
            "Accel_Y": round(random.gauss(0.05, 0.03), 3),
            "Accel_Z": round(random.gauss(0.98, 0.03), 3),
            "Gyro_Magnitude": round(random.gauss(1.4, 0.2), 2),
            "Activity": "STANDING",
            "Standing_Time": "15 min",
            "Alert": "NORMAL",
            "Standing_Time_Num": 15.0
        })

    # Disconnect gap of 40 minutes (> 45s heartbeat timeout)
    # Session 2: 20 min standing (50 mins ago)
    s2_start = now - timedelta(minutes=70)
    for i in range(25):
        t = s2_start + timedelta(seconds=i * 15)
        records.append({
            "created_at": t,
            "entry_id": len(records) + 1,
            "FSR": round(random.gauss(260, 20), 1),
            "Accel_X": round(random.gauss(0.14, 0.05), 3),
            "Accel_Y": round(random.gauss(0.06, 0.04), 3),
            "Accel_Z": round(random.gauss(0.97, 0.04), 3),
            "Gyro_Magnitude": round(random.gauss(1.5, 0.3), 2),
            "Activity": "STANDING",
            "Standing_Time": "20 min",
            "Alert": "WARNING",
            "Standing_Time_Num": 20.0
        })

    # Disconnect gap of 35 minutes
    # Session 3: Active session (10 min standing)
    s3_start = now - timedelta(seconds=15 * 15)
    for i in range(15):
        t = s3_start + timedelta(seconds=i * 15)
        act = "STANDING" if i >= 3 else "SITTING"
        fsr = round(random.gauss(250, 22), 1) if act == "STANDING" else round(random.gauss(50, 10), 1)
        records.append({
            "created_at": t,
            "entry_id": len(records) + 1,
            "FSR": fsr,
            "Accel_X": round(random.gauss(0.11, 0.05), 3),
            "Accel_Y": round(random.gauss(0.04, 0.03), 3),
            "Accel_Z": round(random.gauss(0.98, 0.04), 3),
            "Gyro_Magnitude": round(random.gauss(1.35, 0.25), 2),
            "Activity": act,
            "Standing_Time": "10 min",
            "Alert": "NORMAL",
            "Standing_Time_Num": 10.0
        })

    df = pd.DataFrame(records)
    return df, {"name": "Smart Calf Sense (Simulation)", "id": "DEMO-001"}

# ==============================================================================
# 7. THINGSPEAK API CLIENT
# ==============================================================================

def fetch_thingspeak_data(channel_id, read_api_key=None, results=50):
    if not channel_id or str(channel_id).strip() in ["", "YOUR_CHANNEL_ID", "None"]:
        return None, None, "ThingSpeak Channel ID is not configured."

    url = f"https://api.thingspeak.com/channels/{str(channel_id).strip()}/feeds.json"
    params = {"results": int(results)}

    if read_api_key and str(read_api_key).strip() not in ["", "YOUR_READ_API_KEY", "None"]:
        params["api_key"] = str(read_api_key).strip()

    try:
        response = requests.get(url, params=params, timeout=8)

        if response.status_code == 404:
            return None, None, f"ThingSpeak Channel #{channel_id} not found. Check Channel ID."
        elif response.status_code in [400, 401, 403]:
            return None, None, f"Access denied (HTTP {response.status_code}). Provide a valid Read API Key."
        elif response.status_code != 200:
            return None, None, f"ThingSpeak API error: HTTP {response.status_code}"

        data = response.json()
        if "feeds" not in data or not data["feeds"]:
            return None, data.get("channel", {}), "Channel found, but no feeds have been recorded yet."

        feeds = data["feeds"]
        channel_info = data.get("channel", {})

        parsed_rows = []
        for feed in feeds:
            created_at_str = feed.get("created_at")
            try:
                created_at = pd.to_datetime(created_at_str)
            except Exception:
                created_at = pd.Timestamp.now(tz="UTC")

            fsr = extract_numeric(feed.get("field1"))
            accel_x = extract_numeric(feed.get("field2"))
            accel_y = extract_numeric(feed.get("field3"))
            accel_z = extract_numeric(feed.get("field4"))
            gyro_mag = extract_numeric(feed.get("field5"))
            activity = normalize_activity(feed.get("field6"))

            raw_standing_time = feed.get("field7")
            if raw_standing_time is None or pd.isna(raw_standing_time) or str(raw_standing_time).strip() == "":
                standing_time_str = "0 min"
            else:
                raw_str = str(raw_standing_time).strip()
                standing_time_str = raw_str if "min" in raw_str.lower() or "s" in raw_str.lower() else f"{raw_str} min"
            standing_time_num = extract_numeric(standing_time_str)

            alert = normalize_alert(feed.get("field8"))

            parsed_rows.append({
                "created_at": created_at,
                "entry_id": feed.get("entry_id"),
                "FSR": fsr,
                "Accel_X": accel_x,
                "Accel_Y": accel_y,
                "Accel_Z": accel_z,
                "Gyro_Magnitude": gyro_mag,
                "Activity": activity,
                "Standing_Time": standing_time_str,
                "Alert": alert,
                "Standing_Time_Num": standing_time_num
            })

        df = pd.DataFrame(parsed_rows)
        return df, channel_info, None

    except requests.exceptions.Timeout:
        return None, None, "ThingSpeak API request timed out (server did not respond in 8s)."
    except requests.exceptions.ConnectionError:
        return None, None, "Network error: Unable to connect to ThingSpeak API. Check internet connection."
    except Exception as e:
        return None, None, f"Unexpected error reading ThingSpeak data: {str(e)}"

# ==============================================================================
# 8. SIDEBAR CONTROLS & TEST SUITE
# ==============================================================================

def detect_theme(theme_choice):
    """
    Detects if light theme is active based on:
    1. Explicit sidebar selection ('Light Theme' or 'Dark Theme')
    2. Streamlit's native theme setting (via st.context.theme)
    """
    if theme_choice == "Light Theme":
        return True
    elif theme_choice == "Dark Theme":
        return False

    # Auto mode: check st.context.theme
    try:
        ctx = getattr(st, "context", None)
        if ctx:
            ctx_theme = getattr(ctx, "theme", None)
            if ctx_theme:
                t_type = getattr(ctx_theme, "type", None)
                if not t_type and hasattr(ctx_theme, "get"):
                    t_type = ctx_theme.get("type")
                if t_type and str(t_type).lower() == "light":
                    return True
                if t_type and str(t_type).lower() == "dark":
                    return False

                t_base = getattr(ctx_theme, "base", None)
                if not t_base and hasattr(ctx_theme, "get"):
                    t_base = ctx_theme.get("base")
                if t_base and str(t_base).lower() == "light":
                    return True
                if t_base and str(t_base).lower() == "dark":
                    return False
    except Exception:
        pass

    return False

def render_sidebar(session_manager):
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 8px 0 14px 0;">
            <div style="font-size: 2.8rem;">🦵</div>
            <div class="sidebar-brand-title">SMART CALF SENSE</div>
            <div class="sidebar-brand-sub">IoT Telemetry & Battery Station</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    secret_channel_id = ""
    secret_read_key = ""
    try:
        if "THINGSPEAK_CHANNEL_ID" in st.secrets:
            secret_channel_id = str(st.secrets["THINGSPEAK_CHANNEL_ID"]).strip()
        if "THINGSPEAK_READ_API_KEY" in st.secrets:
            secret_read_key = str(st.secrets["THINGSPEAK_READ_API_KEY"]).strip()
    except Exception:
        pass

    has_valid_secret = bool(secret_channel_id and secret_channel_id != "YOUR_CHANNEL_ID")

    st.sidebar.subheader("📡 Cloud Configuration")
    if has_valid_secret:
        st.sidebar.success(f"🔒 Loaded from Secrets: **#{secret_channel_id}**")
        use_manual = st.sidebar.checkbox("Override Secrets manually", value=False)
    else:
        st.sidebar.info("💡 Set credentials in `.streamlit/secrets.toml` or enter below:")
        use_manual = True

    if use_manual:
        channel_id_input = st.sidebar.text_input("ThingSpeak Channel ID", value=secret_channel_id if secret_channel_id != "YOUR_CHANNEL_ID" else "", placeholder="e.g. 2489012")
        read_key_input = st.sidebar.text_input("Read API Key (if Private)", value=secret_read_key if secret_read_key != "YOUR_READ_API_KEY" else "", type="password", placeholder="e.g. XXXXXXXXXXXXXXXX")
    else:
        channel_id_input = secret_channel_id
        read_key_input = secret_read_key

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Dashboard Appearance")
    theme_choice = st.sidebar.selectbox(
        "Dashboard Theme",
        ["Auto (Sync with Streamlit Theme)", "Light Theme", "Dark Theme"],
        index=0,
        help="Select visual theme. 'Auto' automatically adapts when you switch Light/Dark in Streamlit's top-right Settings menu."
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔋 Battery & Consumption Model")
    
    battery_capacity = st.sidebar.number_input(
        "Battery Capacity (mAh)",
        min_value=500,
        max_value=5000,
        value=2000,
        step=250,
        help="Configurable Li-ion/LiPo capacity. Assumptions: ESP32 active + Wi-Fi ~140mA, Vibration Motor +80mA."
    )

    accel_discharge = st.sidebar.slider(
        "Demo Discharge Rate Multiplier",
        min_value=1.0,
        max_value=10.0,
        value=1.0,
        step=1.0,
        help="Use 3x–5x during short project demonstrations to observe dynamic battery depletion without waiting hours."
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Session & Telemetry Controls")

    default_demo = not bool(channel_id_input and channel_id_input != "YOUR_CHANNEL_ID")
    demo_mode = st.sidebar.toggle("Simulated / Demo Data Mode", value=default_demo)

    heartbeat_timeout = st.sidebar.slider(
        "Heartbeat Timeout (seconds)",
        min_value=30,
        max_value=120,
        value=45,
        step=5,
        help="Disconnection threshold: If no packet arrives within this time, ESP32 is marked DISCONNECTED."
    )
    session_manager.heartbeat_timeout = heartbeat_timeout

    results_count = st.sidebar.slider(
        "Fetch Entry History",
        min_value=15,
        max_value=100,
        value=50,
        step=5,
        help="Number of latest telemetry feeds retrieved from ThingSpeak"
    )

    auto_refresh = st.sidebar.checkbox(
        "Auto-Refresh (every 15s)",
        value=True,
        help="Automatically polls ThingSpeak every 15 seconds complying with rate limits"
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Session Test Controls")

    sim_force_disconnect = st.sidebar.toggle(
        "🔌 Simulate ESP32 Disconnect",
        value=False,
        help="Immediately triggers DISCONNECTED status, freezes current session timer, and preserves Total Standing Time."
    )

    col_btn1, col_btn2 = st.sidebar.columns(2)
    with col_btn1:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Reset Sessions", use_container_width=True, help="Resets all session tracking back to Session 1"):
            session_manager.reset_all()
            st.rerun()

    with st.sidebar.expander("ℹ️ Scientific Assumptions & Hardware"):
        st.markdown(
            """
            **Battery Estimation Model:**
            - **No Hardware Sensor:** There is no fuel gauge IC or ADC divider.
            - **Charge Assumption:** Device is assumed charged to **100%** before each use session.
            - **Consumption Model:**
              - Base active (ESP32+Wi-Fi+MPU6050+FSR): `140 mA`
              - Vibration feedback (Alerts): `+80 mA`
            - **Session Isolation:** Previous session's battery does NOT carry over.
            
            **Hardware Pipeline:**
            - **FSR402:** GPIO 34 (ADC1) + 10kΩ pull-down
            - **MPU6050:** GPIO 21 (SDA), GPIO 22 (SCL)
            - **Vibration/LED:** GPIO 2
            """
        )

    st.sidebar.caption("Smart Calf Sense v3.0 • Final Telemetry Release")
    return channel_id_input, read_key_input, demo_mode, results_count, auto_refresh, sim_force_disconnect, battery_capacity, accel_discharge, theme_choice

# ==============================================================================
# 9. GRAPH GENERATORS (Interactive Plotly Suite)
# ==============================================================================

def create_chart_layout(title, yaxis_title, height=290, is_light=False):
    title_color = "#0f172a" if is_light else "#f1f5f9"
    axis_font_color = "#475569" if is_light else "#94a3b8"
    grid_color = "rgba(226, 232, 240, 0.85)" if is_light else "rgba(148, 163, 184, 0.12)"
    paper_bg = "rgba(255, 255, 255, 0)" if is_light else "rgba(15, 23, 42, 0.4)"
    plot_bg = "rgba(248, 250, 252, 0.9)" if is_light else "rgba(15, 23, 42, 0.7)"

    return go.Layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=13, color=title_color, family="Inter, sans-serif"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        height=height,
        margin=dict(l=48, r=20, t=44, b=35),
        hovermode="x unified",
        xaxis=dict(
            title=dict(text="Time", font=dict(size=11, color=axis_font_color)),
            showgrid=True,
            gridcolor=grid_color,
            tickfont=dict(size=11, color=axis_font_color),
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=yaxis_title, font=dict(size=11, color=axis_font_color)),
            showgrid=True,
            gridcolor=grid_color,
            tickfont=dict(size=11, color=axis_font_color),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=axis_font_color),
            bgcolor="rgba(0,0,0,0)"
        )
    )

# A. FSR vs Time
def plot_fsr_trend(df, is_light=False):
    fig = go.Figure()
    line_col = "#0284c7" if is_light else "#00f2fe"
    marker_col = "#0369a1" if is_light else "#00c9ff"
    fill_col = "rgba(2, 132, 199, 0.12)" if is_light else "rgba(0, 242, 254, 0.12)"

    fig.add_trace(
        go.Scatter(
            x=df["created_at"],
            y=df["FSR"],
            mode="lines+markers",
            name="FSR Value",
            line=dict(color=line_col, width=2.5, shape="spline"),
            marker=dict(size=4, color=marker_col),
            fill="tozeroy",
            fillcolor=fill_col,
            hovertemplate="<b>FSR:</b> %{y:.1f}<extra></extra>"
        )
    )
    fig.update_layout(create_chart_layout("FSR Pressure Trend", "FSR Value", is_light=is_light))
    return fig

# B. Accelerometer (Accel X, Y, Z on same time-series with legend)
def plot_motion_trend(df, is_light=False):
    fig = go.Figure()
    col_x = "#dc2626" if is_light else "#ff6b6b"
    col_y = "#0284c7" if is_light else "#4facfe"
    col_z = "#10b981" if is_light else "#00e676"

    fig.add_trace(go.Scatter(x=df["created_at"], y=df["Accel_X"], mode="lines", name="Accel X", line=dict(color=col_x, width=2)))
    fig.add_trace(go.Scatter(x=df["created_at"], y=df["Accel_Y"], mode="lines", name="Accel Y", line=dict(color=col_y, width=2)))
    fig.add_trace(go.Scatter(x=df["created_at"], y=df["Accel_Z"], mode="lines", name="Accel Z", line=dict(color=col_z, width=2)))
    fig.update_layout(create_chart_layout("Motion / Accelerometer Trend", "Acceleration", is_light=is_light))
    return fig

# C. Gyroscope Activity
def plot_gyro_activity(df, is_light=False):
    fig = go.Figure()
    line_col = "#d97706" if is_light else "#ffd166"
    marker_col = "#b45309" if is_light else "#f59e0b"
    fill_col = "rgba(217, 119, 6, 0.12)" if is_light else "rgba(255, 209, 102, 0.12)"

    fig.add_trace(
        go.Scatter(
            x=df["created_at"],
            y=df["Gyro_Magnitude"],
            mode="lines+markers",
            name="Gyro Magnitude",
            line=dict(color=line_col, width=2, shape="spline"),
            marker=dict(size=4, color=marker_col),
            fill="tozeroy",
            fillcolor=fill_col,
            hovertemplate="<b>Gyro:</b> %{y:.2f} °/s<extra></extra>"
        )
    )
    fig.update_layout(create_chart_layout("Gyroscope Activity", "Angular Rate (°/s)", is_light=is_light))
    return fig

# D. Standing Time Progression
def plot_standing_progression(df, is_light=False):
    fig = go.Figure()
    line_col = "#8b5cf6" if is_light else "#c084fc"
    marker_col = "#7c3aed" if is_light else "#a855f7"
    fill_col = "rgba(139, 92, 246, 0.12)" if is_light else "rgba(168, 85, 247, 0.12)"
    annot_col = "#dc2626" if is_light else "#f87171"

    fig.add_trace(
        go.Scatter(
            x=df["created_at"],
            y=df["Standing_Time_Num"],
            mode="lines+markers",
            name="Session Standing",
            line=dict(color=line_col, width=2.5, shape="hv"),
            marker=dict(size=4, color=marker_col),
            fill="tozeroy",
            fillcolor=fill_col,
            hovertemplate="<b>Standing:</b> %{y:.1f} min<extra></extra>"
        )
    )
    fig.add_hline(y=30, line_dash="dot", line_color="#ef4444", annotation_text="30 min Advisory Limit", annotation_position="bottom right", annotation_font=dict(size=10, color=annot_col))
    fig.update_layout(create_chart_layout("Standing Time Progression", "Standing Duration (min)", is_light=is_light))
    return fig

# E. Activity Timeline
def plot_activity_timeline(df, is_light=False):
    cat_order = ["SITTING", "STANDING", "WALKING", "MOVING", "UNKNOWN"]
    color_map = {
        "SITTING": "#8b5cf6",
        "STANDING": "#2563eb" if is_light else "#3b82f6",
        "WALKING": "#10b981",
        "MOVING": "#0284c7" if is_light else "#06b6d4",
        "UNKNOWN": "#64748b" if is_light else "#94a3b8"
    }

    fig = go.Figure()
    line_col = "rgba(203, 213, 225, 0.8)" if is_light else "rgba(148, 163, 184, 0.4)"
    fig.add_trace(
        go.Scatter(
            x=df["created_at"],
            y=df["Activity"],
            mode="lines+markers",
            name="Activity State",
            line=dict(shape="hv", color=line_col, width=2),
            marker=dict(
                size=9,
                color=[color_map.get(str(a).upper(), "#94a3b8") for a in df["Activity"]],
                line=dict(width=1.5, color="#ffffff")
            ),
            hovertemplate="<b>Time:</b> %{x|%H:%M:%S}<br><b>State:</b> %{y}<extra></extra>"
        )
    )
    fig.update_yaxes(categoryorder="array", categoryarray=cat_order)
    fig.update_layout(create_chart_layout("Activity Timeline & Posture History", "Postural State", is_light=is_light))
    return fig

# F. ESTIMATED BATTERY USAGE
def plot_estimated_battery(battery_trace, is_light=False):
    fig = go.Figure()
    if battery_trace:
        b_df = pd.DataFrame(battery_trace)
        final_pct = b_df["estimated_battery_pct"].iloc[-1]
        line_color = "#10b981" if final_pct > 30 else ("#f59e0b" if final_pct >= 15 else "#ef4444")
        fill_color = "rgba(16, 185, 129, 0.12)" if final_pct > 30 else ("rgba(245, 158, 11, 0.12)" if final_pct >= 15 else "rgba(239, 68, 68, 0.15)")
        annot_warn = "#b45309" if is_light else "#fbbf24"
        annot_crit = "#dc2626" if is_light else "#f87171"

        fig.add_trace(
            go.Scatter(
                x=b_df["created_at"],
                y=b_df["estimated_battery_pct"],
                mode="lines+markers",
                name="Est. Battery %",
                line=dict(color=line_color, width=2.5, shape="spline"),
                marker=dict(size=4, color=line_color),
                fill="tozeroy",
                fillcolor=fill_color,
                hovertemplate="<b>Estimated Battery:</b> %{y:.1f}%<br><b>Consumed:</b> %{customdata[0]} mAh<extra></extra>",
                customdata=b_df[["consumed_mah"]]
            )
        )
        # Warning guide lines
        fig.add_hline(y=30, line_dash="dash", line_color="#f59e0b", annotation_text="30% Low Warning", annotation_position="bottom right", annotation_font=dict(size=9, color=annot_warn))
        fig.add_hline(y=15, line_dash="dot", line_color="#ef4444", annotation_text="15% Very Low", annotation_position="bottom right", annotation_font=dict(size=9, color=annot_crit))
    else:
        empty_text_color = "#64748b" if is_light else "#94a3b8"
        fig.add_annotation(text="Awaiting Current Session Telemetry", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=empty_text_color))

    fig.update_layout(
        create_chart_layout("Estimated Battery Usage (Current Session)", "Estimated Battery %", is_light=is_light),
        yaxis=dict(range=[0, 105])
    )
    return fig

# ==============================================================================
# 10. MAIN DASHBOARD CONTENT RENDERER
# ==============================================================================

def render_dashboard_content(channel_id, read_api_key, demo_mode, results_count, sim_force_disconnect, battery_capacity, accel_discharge, session_manager, is_light=False):
    # 1. Fetch Telemetry Data
    is_simulated = False
    if demo_mode:
        df, channel_meta = generate_simulation_data(num_points=results_count)
        is_simulated = True
    else:
        df, channel_meta, error_msg = fetch_thingspeak_data(channel_id, read_api_key, results=results_count)
        if error_msg:
            st.warning(f"⚠️ {error_msg}\n\nFalling back to simulated multi-session telemetry so you can evaluate the dashboard.")
            df, channel_meta = generate_simulation_data(num_points=results_count)
            is_simulated = True

    if df is None or df.empty:
        st.error("No telemetry data available. Please verify your ThingSpeak connection.")
        return

    # Theme CSS class
    theme_cls = "light-theme" if is_light else "dark-theme"

    # 2. Process Session & Battery Intelligence
    session_data = session_manager.process(
        df,
        is_simulated=is_simulated,
        sim_force_disconnect=sim_force_disconnect,
        battery_capacity=battery_capacity,
        accel_factor=accel_discharge
    )

    conn_status = session_data["connection_status"]
    session_id = session_data["session_id"]
    session_start_raw = session_data["session_start"]
    last_received_raw = session_data["last_data_received"]
    current_session_sec = session_data["current_session_seconds"]
    total_standing_sec = session_data["total_standing_seconds"]
    est_battery_pct = session_data["estimated_battery_pct"]
    battery_consumed_mah = session_data["battery_consumed_mah"]
    battery_trace = session_data["current_session_battery_trace"]
    seconds_since_last = session_data["seconds_since_last"]

    # Timestamps
    if isinstance(session_start_raw, pd.Timestamp):
        session_start_ist = convert_to_ist(session_start_raw)
        session_start_time_str = session_start_ist.strftime("%I:%M %p")
        session_start_full = session_start_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    elif session_start_raw:
        session_start_ist = convert_to_ist(session_start_raw)
        session_start_time_str = session_start_ist.strftime("%I:%M %p")
        session_start_full = session_start_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    else:
        session_start_time_str = "N/A"
        session_start_full = "Awaiting connection"

    if isinstance(last_received_raw, pd.Timestamp):
        last_received_ist = convert_to_ist(last_received_raw)
        last_received_time_str = last_received_ist.strftime("%I:%M %p")
        last_received_full = last_received_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    elif last_received_raw:
        last_received_ist = convert_to_ist(last_received_raw)
        last_received_time_str = last_received_ist.strftime("%I:%M %p")
        last_received_full = last_received_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    else:
        last_received_time_str = "N/A"
        last_received_full = "No packets received"

    elapsed_str = f"{int(seconds_since_last)}s ago" if seconds_since_last is not None and seconds_since_last < 60 else (f"{int(seconds_since_last // 60)}m ago" if seconds_since_last is not None else "N/A")

    # Battery category
    battery_label, battery_color, battery_emoji = get_battery_status_level(est_battery_pct)
    battery_used_pct = round(100.0 - est_battery_pct, 1)

    latest = df.iloc[-1]

    # --------------------------------------------------------------------------
    # DASHBOARD HEADER (Section 14)
    # --------------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="dashboard-header {theme_cls}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h1 class="title-text {theme_cls}">
                        <span>🦵</span> SMART CALF SENSE
                    </h1>
                    <p class="subtitle-text {theme_cls}">IoT-Based Calf Muscle Activity & Prolonged Standing Monitoring</p>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                    <span class="status-badge {'status-connected' if conn_status == 'CONNECTED' else 'status-disconnected'} {theme_cls}">
                        <span class="pulsing-dot"></span> ● {conn_status}
                    </span>
                    <div class="backend-meta-text {theme_cls}">
                        Backend: ThingSpeak ({f'#{channel_id}' if (channel_id and not is_simulated) else 'SIMULATION'}) • Last: {last_received_full} ({elapsed_str})
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # TOP SUMMARY CARDS (Section 15)
    # --------------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    # Color tokens for values
    val_conn_color = ("#10b981" if is_light else "#34d399") if conn_status == "CONNECTED" else ("#ef4444" if is_light else "#f87171")
    val_standing_color = "#8b5cf6" if is_light else "#c084fc"
    val_session_color = "#0284c7" if is_light else "#38bdf8"

    # 1. Connection Status Card
    conn_icon = "🟢" if conn_status == "CONNECTED" else "🔴"
    with c1:
        st.markdown(
            f"""
            <div class="summary-card card-connection {theme_cls}">
                <div class="card-header-label {theme_cls}">
                    <span>CONNECTION</span>
                    <span>{conn_icon}</span>
                </div>
                <div class="card-main-val" style="color: {val_conn_color}; font-size: 1.85rem;">
                    ● {conn_status}
                </div>
                <div>
                    <div class="card-subtitle {theme_cls}">Session #{session_id}</div>
                    <div class="card-footnote {theme_cls}">{'Active transmission' if conn_status == 'CONNECTED' else 'Session ended (Preserved)'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Estimated Battery Card
    with c2:
        st.markdown(
            f"""
            <div class="summary-card card-battery {theme_cls}">
                <div class="card-header-label {theme_cls}">
                    <span>EST. BATTERY</span>
                    <span>🔋</span>
                </div>
                <div class="card-main-val" style="color: {battery_color};">
                    {est_battery_pct:.0f}%
                </div>
                <div>
                    <div class="card-subtitle {theme_cls}">Current session • {battery_used_pct:.0f}% used</div>
                    <div class="card-footnote {theme_cls}">Assumes charged before use</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Total Standing Time Card
    tot_disp = format_friendly_duration(total_standing_sec)
    tot_hms = format_hms(total_standing_sec)
    with c3:
        st.markdown(
            f"""
            <div class="summary-card card-total-standing {theme_cls}">
                <div class="card-header-label {theme_cls}">
                    <span>TOTAL STANDING</span>
                    <span>⏳</span>
                </div>
                <div class="card-main-val" style="color: {val_standing_color};">
                    {tot_disp}
                </div>
                <div>
                    <div class="card-subtitle {theme_cls}">All sessions • {tot_hms}</div>
                    <div class="card-footnote {theme_cls}">Accumulated across sessions</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Current Session Standing Time Card
    curr_disp = format_friendly_duration(current_session_sec)
    curr_hms = format_hms(current_session_sec)
    with c4:
        st.markdown(
            f"""
            <div class="summary-card card-current-session {theme_cls}">
                <div class="card-header-label {theme_cls}">
                    <span>CURRENT SESSION</span>
                    <span>⏱️</span>
                </div>
                <div class="card-main-val" style="color: {val_session_color};">
                    {curr_disp}
                </div>
                <div>
                    <div class="card-subtitle {theme_cls}">Session #{session_id} • {curr_hms}</div>
                    <div class="card-footnote {theme_cls}">Since latest connection</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # CURRENT SESSION DETAILS (Section 20)
    # --------------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="session-details-box {theme_cls}">
            <div>
                <div class="session-item-label {theme_cls}">SESSION</div>
                <div class="session-item-val val-blue {theme_cls}">#{session_id}</div>
            </div>
            <div>
                <div class="session-item-label {theme_cls}">SESSION STARTED</div>
                <div class="session-item-val val-primary {theme_cls}">{session_start_time_str}</div>
            </div>
            <div>
                <div class="session-item-label {theme_cls}">LAST DATA</div>
                <div class="session-item-val val-primary {theme_cls}">{last_received_time_str}</div>
            </div>
            <div>
                <div class="session-item-label {theme_cls}">CURRENT STANDING</div>
                <div class="session-item-val val-blue {theme_cls}">{curr_hms}</div>
            </div>
            <div>
                <div class="session-item-label {theme_cls}">ESTIMATED BATTERY</div>
                <div class="session-item-val" style="color: {battery_color};">{est_battery_pct:.0f}% ({battery_label})</div>
            </div>
            <div>
                <div class="session-item-label {theme_cls}">HEARTBEAT TIMEOUT</div>
                <div class="session-item-val val-amber {theme_cls}">{session_manager.heartbeat_timeout}s</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if conn_status == "DISCONNECTED":
        st.markdown(
            f"""
            <div class="connection-alert-box {theme_cls}">
                <span class="connection-alert-icon">🔴</span>
                <div>
                    <div class="connection-alert-title {theme_cls}">
                        ● DISCONNECTED — SESSION ENDED <span style="font-weight: normal; font-size: 0.88rem;">(No data packet received for > {session_manager.heartbeat_timeout}s).</span>
                    </div>
                    <div class="connection-alert-desc {theme_cls}">
                        Current session timer is stopped. Total Standing Time ({tot_disp}) is preserved. When the ESP32 reconnects, a <b>NEW SESSION</b> (Session #{session_id + 1}) will begin, resetting Current Session Standing Time to 00:00:00 and Estimated Battery to 100%.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # ACTIVITY STATUS & ALERT (Section 16)
    # --------------------------------------------------------------------------
    st.markdown(f'<div class="section-title {theme_cls}"><span class="icon">🏃</span> Activity & Alert Monitoring</div>', unsafe_allow_html=True)
    
    act_col1, act_col2 = st.columns([1, 2])
    activity_val = str(latest["Activity"]).upper()
    act_badge_cls = get_activity_badge_class(activity_val)
    act_icon = get_activity_icon(activity_val)

    alert_val = str(latest["Alert"]).upper()
    alert_color = "#34d399" if "NORM" in alert_val else ("#fbbf24" if "WARN" in alert_val else "#f87171")
    alert_icon = "✅" if "NORM" in alert_val else ("⚠️" if "WARN" in alert_val else "🚨")

    with act_col1:
        st.markdown(
            f"""
            <div class="activity-card {theme_cls}">
                <div class="activity-card-label {theme_cls}">CURRENT DETECTED ACTIVITY</div>
                <div style="margin-top: 10px; margin-bottom: 8px;">
                    <span class="activity-badge {act_badge_cls} {theme_cls}">{act_icon} {activity_val}</span>
                </div>
                <div class="activity-card-desc {theme_cls}">Directly classified from ThingSpeak Field 6.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with act_col2:
        if "ALERT" in alert_val:
            banner_class = "alert-alert"
            banner_title = "PROLONGED STANDING ALERT"
            banner_desc = "Critical standing threshold exceeded! Risk of venous stasis and calf muscle fatigue. ESP32 haptic feedback prompt active. Action: Take a seat or perform active calf raises."
        elif "WARN" in alert_val:
            banner_class = "alert-warning"
            banner_title = "PROLONGED STANDING WARNING"
            banner_desc = "Continuous standing approaching ergonomic fatigue limit. Action: Shift weight between legs, take short walking steps to activate venous muscle pump."
        else:
            banner_class = "alert-normal"
            banner_title = "NORMAL POSTURAL DYNAMICS"
            banner_desc = "Calf muscle contractions and posture are within healthy parameters. Skeletal muscle venous return active."

        st.markdown(
            f"""
            <div class="alert-banner {banner_class} {theme_cls}" style="margin: 0; height: 100%;">
                <div style="font-size: 2.2rem; flex-shrink: 0;">{alert_icon}</div>
                <div style="flex-grow: 1;">
                    <div class="alert-banner-title">
                        {alert_val} — {banner_title}
                    </div>
                    <div class="alert-banner-desc">
                        {banner_desc}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # LIVE SENSOR DATA (Section 19)
    # --------------------------------------------------------------------------
    st.markdown(f'<div class="section-title {theme_cls}"><span class="icon">🧭</span> Live Sensor Data (MPU6050 + FSR402)</div>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.columns(5)

    fsr_col = "#0284c7" if is_light else "#38bdf8"
    acc_x_col = "#dc2626" if is_light else "#ff6b6b"
    acc_y_col = "#2563eb" if is_light else "#4facfe"
    acc_z_col = "#16a34a" if is_light else "#00e676"
    gyro_col = "#d97706" if is_light else "#ffd166"
    unit_col = "#64748b" if is_light else "#94a3b8"

    with s1:
        st.markdown(
            f"""
            <div class="sensor-card {theme_cls}">
                <div class="sensor-card-label {theme_cls}">FSR (CALF PRESSURE)</div>
                <div class="sensor-card-val" style="color: {fsr_col};">{latest['FSR']:.0f}</div>
                <div class="sensor-card-sub {theme_cls}">ADC / Tension Value</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            f"""
            <div class="sensor-card {theme_cls}">
                <div class="sensor-card-label {theme_cls}">ACCELEROMETER X</div>
                <div class="sensor-card-val" style="color: {acc_x_col};">{latest['Accel_X']:+.3f} <span style="font-size: 0.8rem; color: {unit_col};">g</span></div>
                <div class="sensor-card-sub {theme_cls}">Lateral Axis</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            f"""
            <div class="sensor-card {theme_cls}">
                <div class="sensor-card-label {theme_cls}">ACCELEROMETER Y</div>
                <div class="sensor-card-val" style="color: {acc_y_col};">{latest['Accel_Y']:+.3f} <span style="font-size: 0.8rem; color: {unit_col};">g</span></div>
                <div class="sensor-card-sub {theme_cls}">Anterior-Posterior</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s4:
        st.markdown(
            f"""
            <div class="sensor-card {theme_cls}">
                <div class="sensor-card-label {theme_cls}">ACCELEROMETER Z</div>
                <div class="sensor-card-val" style="color: {acc_z_col};">{latest['Accel_Z']:+.3f} <span style="font-size: 0.8rem; color: {unit_col};">g</span></div>
                <div class="sensor-card-sub {theme_cls}">Vertical Gravity Axis</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with s5:
        st.markdown(
            f"""
            <div class="sensor-card {theme_cls}">
                <div class="sensor-card-label {theme_cls}">GYRO MAGNITUDE</div>
                <div class="sensor-card-val" style="color: {gyro_col};">{latest['Gyro_Magnitude']:.2f} <span style="font-size: 0.8rem; color: {unit_col};">°/s</span></div>
                <div class="sensor-card-sub {theme_cls}">Angular Velocity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # INTERACTIVE SENSOR & TELEMETRY GRAPHS (Sections 17 & 18)
    # --------------------------------------------------------------------------
    st.markdown(f'<div class="section-title {theme_cls}"><span class="icon">📈</span> Interactive Telemetry & Intelligence Graphs</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 Biomechanical Dynamics (FSR & Standing)",
        "🧭 3D Motion (MPU6050 Accel & Gyro)",
        "🔋 Activity Timeline & Estimated Battery"
    ])

    with tab1:
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(plot_fsr_trend(df, is_light=is_light), use_container_width=True, config={"displayModeBar": False})
        with g2:
            st.plotly_chart(plot_standing_progression(df, is_light=is_light), use_container_width=True, config={"displayModeBar": False})

    with tab2:
        g3, g4 = st.columns(2)
        with g3:
            st.plotly_chart(plot_motion_trend(df, is_light=is_light), use_container_width=True, config={"displayModeBar": False})
        with g4:
            st.plotly_chart(plot_gyro_activity(df, is_light=is_light), use_container_width=True, config={"displayModeBar": False})

    with tab3:
        g5, g6 = st.columns(2)
        with g5:
            st.plotly_chart(plot_activity_timeline(df, is_light=is_light), use_container_width=True, config={"displayModeBar": False})
        with g6:
            st.plotly_chart(plot_estimated_battery(battery_trace, is_light=is_light), use_container_width=True, config={"displayModeBar": False})

    # --------------------------------------------------------------------------
    # HISTORICAL SENSOR DATA & CSV EXPORT (Section 21)
    # --------------------------------------------------------------------------
    with st.expander("📋 HISTORICAL SENSOR DATA (Interactive Records & Export)", expanded=False):
        export_df = df[[
            "created_at", "FSR", "Accel_X", "Accel_Y", "Accel_Z",
            "Gyro_Magnitude", "Activity", "Standing_Time", "Alert"
        ]].copy()

        # Add estimated battery column for transparency
        export_df["Estimated_Battery"] = f"{est_battery_pct:.0f}%"

        export_df.rename(columns={
            "created_at": "Timestamp",
            "Accel_X": "Accel X (g)",
            "Accel_Y": "Accel Y (g)",
            "Accel_Z": "Accel Z (g)",
            "Gyro_Magnitude": "Gyro Mag (°/s)",
            "Standing_Time": "Standing Time",
            "Estimated_Battery": "Est. Battery"
        }, inplace=True)

        display_df = export_df.sort_values(by="Timestamp", ascending=False).reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True, height=280)

        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        d_col1, d_col2 = st.columns([1, 4])
        with d_col1:
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_bytes,
                file_name=f"smart_calf_sense_telemetry_{timestamp_str}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d_col2:
            st.caption(f"Displaying the latest {len(df)} records fetched via ThingSpeak API. Includes session-estimated battery consumption.")

    # --------------------------------------------------------------------------
    # SESSION LOG EXPANDER
    # --------------------------------------------------------------------------
    sessions_hist = session_data.get("sessions_history", [])
    if sessions_hist:
        with st.expander(f"📑 Session History Log ({len(sessions_hist)} Sessions Recorded)"):
            sess_rows = []
            for s in sessions_hist:
                st_time = s["start_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(s["start_time"], pd.Timestamp) else str(s["start_time"])[:19]
                en_time = s["end_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(s["end_time"], pd.Timestamp) else str(s["end_time"])[:19]
                sess_rows.append({
                    "Session ID": f"Session #{s['session_id']}",
                    "Status": "🟢 ACTIVE" if s.get("is_active") and conn_status == "CONNECTED" else "⚪ CONCLUDED",
                    "Started": st_time,
                    "Last Data": en_time,
                    "Standing Time": format_friendly_duration(s["standing_seconds"]),
                    "Standing Time (HH:MM:SS)": format_hms(s["standing_seconds"]),
                    "Packets": s["feed_count"]
                })
            sess_table_df = pd.DataFrame(sess_rows)
            st.dataframe(sess_table_df, use_container_width=True, hide_index=True)

# ==============================================================================
# 11. MAIN APPLICATION ENTRYPOINT & REFRESH RUNNER
# ==============================================================================

def main():
    session_manager = SessionManager(
        history_file=".streamlit/session_history.json",
        heartbeat_timeout=45
    )

    channel_id, read_api_key, demo_mode, results_count, auto_refresh, sim_force_disconnect, battery_capacity, accel_discharge, theme_choice = render_sidebar(session_manager)

    is_light = detect_theme(theme_choice)

    refresh_interval = 15 if auto_refresh else None

    @st.fragment(run_every=refresh_interval)
    def live_telemetry_fragment():
        render_dashboard_content(
            channel_id=channel_id,
            read_api_key=read_api_key,
            demo_mode=demo_mode,
            results_count=results_count,
            sim_force_disconnect=sim_force_disconnect,
            battery_capacity=battery_capacity,
            accel_discharge=accel_discharge,
            session_manager=session_manager,
            is_light=is_light
        )

    live_telemetry_fragment()

if __name__ == "__main__":
    main()
