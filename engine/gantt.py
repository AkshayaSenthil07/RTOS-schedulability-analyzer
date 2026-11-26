
from pathlib import Path
from html import escape


def generate_gantt_svg(
    result: dict,
    output_path: str,
    duration: int
) -> None:
    """
    Generate an SVG Gantt chart from event-simulator records.

    Displays:
    - Task execution intervals
    - Idle intervals
    - Preemption timestamps
    - Missed deadline markers
    """

    if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
        raise ValueError("Duration must be a positive integer")

    intervals = result.get("intervals", [])
    preemptions = result.get("preemptions", [])
    jobs = result.get("jobs", [])

    if not intervals:
        raise ValueError("Simulation result contains no intervals")

    if any(
        interval["start"] < 0
        or interval["end"] <= interval["start"]
        or interval["end"] > duration
        for interval in intervals
    ):
        raise ValueError("Invalid interval boundaries")

    width = 1100
    left = 80
    right = 40
    plot_width = width - left - right

    lane_y = 115
    lane_height = 60
    chart_bottom = lane_y + lane_height

    colors = [
        "#2563eb",
        "#0d9488",
        "#9333ea",
        "#d97706",
        "#0891b2",
        "#db2777",
    ]

    task_names = sorted({
        interval["task"]
        for interval in intervals
        if interval["task"] is not None
    })

    color_map = {
        name: colors[index % len(colors)]
        for index, name in enumerate(task_names)
    }

    def x_position(time):
        return left + (time / duration) * plot_width

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="320" viewBox="0 0 {width} 320">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="80" y="38" font-size="23" font-weight="bold" '
        'fill="#111827">CPU Execution Gantt Chart</text>',
        '<text x="80" y="65" font-size="13" fill="#6b7280">'
        f'Timeline: 0 to {duration} microseconds</text>',
        '<text x="20" y="150" font-size="14" '
        'font-weight="bold" fill="#111827">CPU</text>',
    ]
        # Draw legend.
    legend_y = 280
    legend_x = left

    for task_name in task_names:
        svg.append(
            f'<rect x="{legend_x}" y="{legend_y - 12}" '
            f'width="14" height="14" '
            f'fill="{color_map[task_name]}"/>'
        )

        svg.append(
            f'<text x="{legend_x + 20}" y="{legend_y}" '
            f'font-size="12" fill="#374151">'
            f'{escape(str(task_name))}</text>'
        )

        legend_x += 100

    # Idle legend.
    svg.append(
        f'<rect x="{legend_x}" y="{legend_y - 12}" '
        'width="14" height="14" fill="#9ca3af"/>'
    )

    svg.append(
        f'<text x="{legend_x + 20}" y="{legend_y}" '
        'font-size="12" fill="#374151">Idle</text>'
    )

    legend_x += 100

    # Preemption legend.
    svg.append(
        f'<line x1="{legend_x}" y1="{legend_y - 7}" '
        f'x2="{legend_x + 20}" y2="{legend_y - 7}" '
        'stroke="#d97706" stroke-width="2" stroke-dasharray="4,3"/>'
    )

    svg.append(
        f'<text x="{legend_x + 26}" y="{legend_y}" '
        'font-size="12" fill="#374151">Preemption</text>'
    )

    legend_x += 130

    # Deadline-miss legend.
    svg.append(
        f'<line x1="{legend_x}" y1="{legend_y - 7}" '
        f'x2="{legend_x + 20}" y2="{legend_y - 7}" '
        'stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3"/>'
    )

    svg.append(
        f'<text x="{legend_x + 26}" y="{legend_y}" '
        'font-size="12" fill="#374151">Deadline miss</text>'
    )

    # Draw the CPU lane background.
    svg.append(
        f'<rect x="{left}" y="{lane_y}" '
        f'width="{plot_width}" height="{lane_height}" '
        'fill="#f3f4f6" stroke="#9ca3af"/>'
    )

    # Draw execution and idle intervals.
    for interval in intervals:

        start = interval["start"]
        end = interval["end"]

        x = x_position(start)
        segment_width = x_position(end) - x

        task = interval["task"]
        kind = interval["kind"]

        if kind == "idle" or task is None:
            color = "#9ca3af"
            label = "Idle"
        else:
            color = color_map.get(task, "#64748b")
            label = escape(str(task))

        svg.append(
            f'<rect x="{x:.2f}" y="{lane_y}" '
            f'width="{segment_width:.2f}" height="{lane_height}" '
            f'fill="{color}" stroke="#ffffff" stroke-width="1">'
            f'<title>{label}: {start}–{end} µs</title></rect>'
        )

        if segment_width >= 28:
            svg.append(
                f'<text x="{x + segment_width / 2:.2f}" '
                f'y="{lane_y + 35}" text-anchor="middle" '
                f'font-size="13" font-weight="bold" fill="#ffffff">'
                f'{label}</text>'
            )

    # Draw preemption markers.
    for preemption in preemptions:

        time = preemption["time"]

        if 0 <= time <= duration:
            x = x_position(time)

            svg.append(
                f'<line x1="{x:.2f}" y1="{lane_y - 15}" '
                f'x2="{x:.2f}" y2="{chart_bottom + 8}" '
                'stroke="#d97706" stroke-width="2" '
                'stroke-dasharray="4,3">'
                '<title>Preemption</title></line>'
            )

    # Draw missed-deadline markers.
    missed_jobs = [
        job for job in jobs
        if job["deadline_missed"]
    ]

    for index, job in enumerate(missed_jobs):

        deadline = job["deadline"]

        if 0 <= deadline <= duration:
            x = x_position(deadline)

            svg.append(
                f'<line x1="{x:.2f}" y1="{lane_y - 22}" '
                f'x2="{x:.2f}" y2="{chart_bottom + 12}" '
                'stroke="#dc2626" stroke-width="2.5" '
                'stroke-dasharray="5,3">'
                '<title>Missed deadline</title></line>'
            )

            svg.append(
                f'<text x="{x + 3:.2f}" '
                f'y="{lane_y - 28 - (index % 3) * 13}" '
                'font-size="10" fill="#dc2626">'
                f'{escape(str(job["task"]))} deadline</text>'
            )

    # Draw timeline axis and tick labels.
    svg.append(
        f'<line x1="{left}" y1="{chart_bottom + 15}" '
        f'x2="{left + plot_width}" y2="{chart_bottom + 15}" '
        'stroke="#111827"/>'
    )

    tick_count = min(10, duration)

    for index in range(tick_count + 1):

        time = duration * index / tick_count
        x = x_position(time)

        svg.append(
            f'<line x1="{x:.2f}" y1="{chart_bottom + 12}" '
            f'x2="{x:.2f}" y2="{chart_bottom + 19}" '
            'stroke="#111827"/>'
        )

        svg.append(
            f'<text x="{x:.2f}" y="{chart_bottom + 37}" '
            'text-anchor="middle" font-size="11" fill="#374151">'
            f'{time:g}</text>'
        )

    svg.append(
        f'<text x="{width / 2}" y="245" text-anchor="middle" '
        'font-size="13" fill="#374151">Time (µs)</text>'
    )

    svg.append('</svg>')

    Path(output_path).write_text(
        "\n".join(svg),
        encoding="utf-8"
    )
