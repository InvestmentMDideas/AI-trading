"""
Dashboard Layout Components
Reusable UI components for the unified dashboard.
"""

from dash import html, dcc
import plotly.graph_objects as go
from typing import Dict, Any, List


def create_header(symbol: str, price: float, change_pct: float) -> html.Div:
    """Create dashboard header with symbol and price."""
    
    color = 'green' if change_pct >= 0 else 'red'
    arrow = '↑' if change_pct >= 0 else '↓'
    
    return html.Div([
        html.H2([
            f"🎯 AI TRADING COMPANION - {symbol} | ",
            html.Span(f"${price:.2f} ", style={'color': color}),
            html.Span(f"{arrow}{abs(change_pct):.2f}%", style={'color': color, 'fontSize': '0.8em'})
        ], style={'margin': '10px', 'textAlign': 'center'})
    ])


def create_metric_card(title: str, value: str, subtitle: str = "", color: str = "#2c3e50") -> html.Div:
    """Create a metric card display."""
    
    return html.Div([
        html.H4(title, style={'color': '#7f8c8d', 'fontSize': '0.9em', 'marginBottom': '5px'}),
        html.H2(value, style={'color': color, 'margin': '5px 0'}),
        html.P(subtitle, style={'color': '#95a5a6', 'fontSize': '0.85em', 'margin': '0'})
    ], style={
        'padding': '15px',
        'backgroundColor': '#ecf0f1',
        'borderRadius': '8px',
        'textAlign': 'center',
        'minHeight': '100px'
    })


def create_probability_bar(probability: float, quality: str) -> html.Div:
    """Create probability score visualization."""
    
    # Color based on quality
    if quality == 'HIGH':
        color = '#27ae60'
    elif quality == 'MEDIUM':
        color = '#f39c12'
    else:
        color = '#e74c3c'
    
    return html.Div([
        html.Div([
            html.Span(f"{probability:.0f}%", style={'fontWeight': 'bold', 'fontSize': '1.2em'}),
            html.Span(f" {quality}", style={'color': color, 'marginLeft': '10px'})
        ]),
        html.Div([
            html.Div(style={
                'width': f'{probability}%',
                'height': '20px',
                'backgroundColor': color,
                'borderRadius': '10px',
                'transition': 'width 0.5s'
            })
        ], style={
            'width': '100%',
            'height': '20px',
            'backgroundColor': '#ecf0f1',
            'borderRadius': '10px',
            'marginTop': '10px'
        })
    ])


def create_score_breakdown(breakdown: Dict[str, float], max_scores: Dict[str, int]) -> html.Div:
    """Create score breakdown visualization."""
    
    items = []
    for name, score in breakdown.items():
        max_score = max_scores.get(name, 20)
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        # Color based on percentage
        if percentage >= 75:
            color = '#27ae60'
        elif percentage >= 50:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        
        items.append(html.Div([
            html.Div([
                html.Span(name.upper(), style={'fontSize': '0.85em', 'color': '#7f8c8d'}),
                html.Span(f"{score}/{max_score}", style={'float': 'right', 'fontWeight': 'bold'})
            ]),
            html.Div([
                html.Div(style={
                    'width': f'{percentage}%',
                    'height': '8px',
                    'backgroundColor': color,
                    'borderRadius': '4px'
                })
            ], style={
                'width': '100%',
                'height': '8px',
                'backgroundColor': '#ecf0f1',
                'borderRadius': '4px',
                'marginTop': '5px',
                'marginBottom': '10px'
            })
        ]))
    
    return html.Div(items)


def create_scenario_card(scenario_name: str, scenario_data: Dict[str, Any], 
                        is_recommended: bool = False) -> html.Div:
    """Create scenario analysis card."""
    
    action = scenario_data.get('action', 'WAIT')
    confidence = scenario_data.get('confidence', 0)
    reasoning = scenario_data.get('reasoning', 'No reasoning provided')
    entry = scenario_data.get('entry')
    stop = scenario_data.get('stop')
    target = scenario_data.get('target')
    size = scenario_data.get('size', 0)
    
    # Colors
    if action == 'WAIT':
        action_color = '#95a5a6'
    elif 'LONG' in action:
        action_color = '#27ae60'
    elif 'SHORT' in action:
        action_color = '#e74c3c'
    else:
        action_color = '#3498db'
    
    border_style = '3px solid #3498db' if is_recommended else '1px solid #bdc3c7'
    
    content = [
        html.H4([
            scenario_name.upper(),
            html.Span(" ⭐ RECOMMENDED", style={'color': '#3498db', 'fontSize': '0.7em', 'marginLeft': '10px'}) 
                if is_recommended else None
        ], style={'color': '#2c3e50', 'marginBottom': '10px'}),
        
        html.Div([
            html.Strong("ACTION: "),
            html.Span(action, style={'color': action_color, 'fontSize': '1.1em'})
        ], style={'marginBottom': '5px'}),
        
        html.Div([
            html.Strong("Confidence: "),
            html.Span(f"{confidence}%", style={'color': '#3498db'})
        ], style={'marginBottom': '10px'}) if action != 'WAIT' else None,
    ]
    
    # Add trade details if not WAIT
    if action != 'WAIT' and entry:
        content.extend([
            html.Div([
                html.Span(f"Entry: ${entry:.2f}", style={'marginRight': '15px'}),
                html.Span(f"Stop: ${stop:.2f}", style={'marginRight': '15px'}),
                html.Span(f"Target: ${target:.2f}")
            ], style={'fontSize': '0.9em', 'color': '#7f8c8d', 'marginBottom': '5px'}),
            
            html.Div([
                html.Span(f"Size: {size} shares")
            ], style={'fontSize': '0.9em', 'color': '#7f8c8d', 'marginBottom': '10px'})
        ])
    
    content.append(
        html.Div([
            html.Strong("Why: "),
            html.Span(reasoning, style={'color': '#34495e'})
        ], style={'fontSize': '0.9em', 'fontStyle': 'italic'})
    )
    
    return html.Div(content, style={
        'padding': '15px',
        'backgroundColor': '#ecf0f1',
        'borderRadius': '8px',
        'border': border_style,
        'marginBottom': '10px'
    })


def create_l2_table(bids: List[Dict], asks: List[Dict]) -> html.Div:
    """Create Level 2 order book table."""
    
    if not bids and not asks:
        return html.Div("No Level 2 data available", style={'textAlign': 'center', 'padding': '20px'})
    
    max_rows = max(len(bids), len(asks), 10)
    
    rows = []
    for i in range(max_rows):
        # Bid side
        if i < len(bids):
            bid = bids[i]
            bid_size = bid['size']
            bid_price = f"${bid['price']:.2f}"
            bid_bg = '#d5f4e6'  # Light green
        else:
            bid_size = ''
            bid_price = ''
            bid_bg = 'transparent'
        
        # Ask side
        if i < len(asks):
            ask = asks[i]
            ask_size = ask['size']
            ask_price = f"${ask['price']:.2f}"
            ask_bg = '#fadbd8'  # Light red
        else:
            ask_size = ''
            ask_price = ''
            ask_bg = 'transparent'
        
        rows.append(html.Tr([
            html.Td(bid_size, style={'textAlign': 'right', 'backgroundColor': bid_bg, 'padding': '5px'}),
            html.Td(bid_price, style={'textAlign': 'center', 'backgroundColor': bid_bg, 'padding': '5px', 'fontWeight': 'bold'}),
            html.Td(ask_price, style={'textAlign': 'center', 'backgroundColor': ask_bg, 'padding': '5px', 'fontWeight': 'bold'}),
            html.Td(ask_size, style={'textAlign': 'left', 'backgroundColor': ask_bg, 'padding': '5px'})
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Bid Size", style={'textAlign': 'right', 'padding': '10px', 'backgroundColor': '#27ae60', 'color': 'white'}),
            html.Th("Bid Price", style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#27ae60', 'color': 'white'}),
            html.Th("Ask Price", style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'}),
            html.Th("Ask Size", style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#e74c3c', 'color': 'white'})
        ])),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '0.9em'})


def create_status_indicator(status: str, message: str) -> html.Div:
    """Create status indicator."""
    
    colors = {
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'info': '#3498db'
    }
    
    icons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    color = colors.get(status, '#95a5a6')
    icon = icons.get(status, '•')
    
    return html.Div([
        html.Span(icon, style={'marginRight': '5px'}),
        html.Span(message)
    ], style={
        'padding': '10px',
        'backgroundColor': color + '20',  # Add transparency
        'border': f'1px solid {color}',
        'borderRadius': '5px',
        'color': color,
        'fontSize': '0.9em',
        'marginBottom': '10px'
    })


def create_empty_state(message: str) -> html.Div:
    """Create empty state placeholder."""
    
    return html.Div([
        html.Div("📊", style={'fontSize': '3em', 'marginBottom': '10px'}),
        html.P(message, style={'color': '#95a5a6', 'fontSize': '1.1em'})
    ], style={
        'textAlign': 'center',
        'padding': '50px',
        'backgroundColor': '#ecf0f1',
        'borderRadius': '8px'
    })
