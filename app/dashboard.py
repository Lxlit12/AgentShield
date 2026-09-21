from fastapi.responses import HTMLResponse


def create_dashboard(events):
    total_events = len(events)

    successful = sum(
        1 for event in events
        if event.get("status") == "success"
    )

    blocked = sum(
        1 for event in events
        if event.get("decision") == "BLOCK"
    )

    reviewed = sum(
        1 for event in events
        if event.get("decision") == "REVIEW"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgentShield Security Dashboard</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }}

            h1 {{
                margin-bottom: 30px;
            }}

            .cards {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                min-width: 180px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }}

            .number {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #eee;
            }}
        </style>
    </head>

    <body>

        <h1>AgentShield Security Dashboard</h1>

        <div class="cards">

            <div class="card">
                <div>Total Events</div>
                <div class="number">{total_events}</div>
            </div>

            <div class="card">
                <div>Successful</div>
                <div class="number">{successful}</div>
            </div>

            <div class="card">
                <div>Blocked</div>
                <div class="number">{blocked}</div>
            </div>

            <div class="card">
                <div>Review</div>
                <div class="number">{reviewed}</div>
            </div>

        </div>

        <h2>Recent Audit Events</h2>

        <table>
            <tr>
                <th>Timestamp</th>
                <th>Session</th>
                <th>Role</th>
                <th>Tool</th>
                <th>Status</th>
                <th>Risk</th>
                <th>Decision</th>
                <th>Egress</th>
            </tr>
    """

    for event in events:
        html += f"""
            <tr>
                <td>{event.get("timestamp")}</td>
                <td>{event.get("session_id")}</td>
                <td>{event.get("role")}</td>
                <td>{event.get("tool")}</td>
                <td>{event.get("status")}</td>
                <td>
                    {event.get("risk_level")}
                    ({event.get("risk_score")})
                </td>
                <td>{event.get("decision")}</td>
                <td>{event.get("egress")}</td>
            </tr>
        """

    html += """
        </table>

    </body>
    </html>
    """

    return HTMLResponse(content=html)