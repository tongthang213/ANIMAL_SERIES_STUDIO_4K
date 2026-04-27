import flet as ft
import os
import json
import subprocess
import re


def main(page: ft.Page):
    # Cấu hình phông chữ chuyên nghiệp
    page.fonts = {
        "Montserrat": "https://fonts.gstatic.com/s/montserrat/v25/JTUSjIg1_i6t8kCHKm459Wlhyw.ttf",
        "OpenSans": "https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf"
    }

    page.title = "Animal Video Portfolio - 4K Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1450
    page.window_height = 950
    page.padding = 25
    page.theme = ft.Theme(font_family="OpenSans")

    DATA_FILE = "data_video_studio.json"
    all_rows_data = []
    entries_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def save_data(e=None):
        data_to_save = {
            "format": format_selector.value,
            "rows": []
        }
        for r in all_rows_data:
            data_to_save["rows"].append({
                "video": r["video"].value,
                "title": r["title"].value,
                "desc": r["desc"].value,
                "theme": r["theme"].value,
                "label": r["label"].value
            })
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def on_change_handler(e):
        save_data()

    def create_video_row(video_val="", title_val="", desc_val="", theme_val="Rừng", label_val=""):
        f1 = ft.TextField(
            label="Video (File .mp4 hoặc Link YouTube)",
            width=350,
            value=video_val,
            on_change=on_change_handler,
            border_color="orange",
            hint_text="vd: lion.mp4 hoặc https://youtu.be/..."
        )
        f2 = ft.TextField(label="Tiêu đề video", width=200, value=title_val, on_change=on_change_handler)
        f3 = ft.TextField(label="Mô tả nội dung", expand=True, value=desc_val, on_change=on_change_handler)
        f_label = ft.TextField(label="Nhãn vùng đất", width=150, value=label_val if label_val else theme_val,
                               on_change=on_change_handler)
        f_theme = ft.Dropdown(
            label="Tông màu", width=130, value=theme_val,
            options=[
                ft.dropdown.Option("Rừng"), ft.dropdown.Option("Biển"),
                ft.dropdown.Option("Sa mạc"), ft.dropdown.Option("Tuyết"), ft.dropdown.Option("Núi lửa"),
            ]
        )
        f_theme.on_change = on_change_handler

        row_content = ft.Row([
            f1, f2, f3, f_label, f_theme,
            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red400",
                          on_click=lambda _: remove_row(row_container))
        ])

        row_container = ft.Container(content=row_content, padding=15, border=ft.Border.all(1, ft.Colors.WHITE12),
                                     border_radius=12, bgcolor=ft.Colors.WHITE10)
        row_entry = {"video": f1, "title": f2, "desc": f3, "label": f_label, "theme": f_theme, "ui": row_container}
        all_rows_data.append(row_entry)
        return row_container

    def remove_row(ui_element):
        for r in all_rows_data:
            if r["ui"] == ui_element:
                all_rows_data.remove(r)
                break
        entries_container.controls.remove(ui_element)
        save_data()
        page.update()

    def add_more(e):
        entries_container.controls.append(create_video_row())
        save_data()
        page.update()

    format_selector = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="horizontal", label="🎬 Ngang (16:9)"),
            ft.Radio(value="vertical", label="📱 Dọc (9:16)"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
        value="horizontal", on_change=on_change_handler
    )

    def load_saved_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                format_selector.value = data.get("format", "horizontal")
                for r_data in data.get("rows", []):
                    entries_container.controls.append(
                        create_video_row(r_data.get("video", ""), r_data.get("title", ""), r_data.get("desc", ""),
                                         r_data.get("theme", "Rừng"), r_data.get("label", "")))
                return True
            except Exception:
                pass
        return False

    if not load_saved_data():
        for _ in range(2): entries_container.controls.append(create_video_row())

    def get_youtube_id(url):
        pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def generate_html_content():
        is_vertical = format_selector.value == "vertical"
        items_html = ""
        theme_map = {"Rừng": "#4CAF50", "Biển": "#00BCD4", "Sa mạc": "#FFC107", "Tuyết": "#E0F7FA",
                     "Núi lửa": "#FF5722"}

        for r in all_rows_data:
            video_input, title = r["video"].value.strip(), r["title"].value.strip()
            desc, label = r["desc"].value.strip(), r["label"].value.strip()
            color = theme_map.get(r["theme"].value, "#ffffff")

            if video_input and title:
                yt_id = get_youtube_id(video_input)
                if yt_id:
                    media_html = f'''
                    <div class="video-bg">
                        <iframe src="https://www.youtube.com/embed/{yt_id}?autoplay=1&mute=1&loop=1&playlist={yt_id}&controls=0&showinfo=0&rel=0&modestbranding=1" 
                                frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
                    </div>'''
                else:
                    media_html = f'''
                    <div class="video-bg">
                        <video autoplay muted loop playsinline>
                            <source src="assets/{video_input}" type="video/mp4">
                        </video>
                    </div>'''

                items_html += f'''
                <div class="item">
                    {media_html}
                    <div class="overlay"></div>
                    <div class="content">
                        {f'<div class="tag" style="background:{color}">{label}</div>' if label else ''}
                        <div class="name" style="border-left:10px solid {color}">{title}</div>
                        <div class="des">{desc}</div>
                    </div>
                </div>'''

        # Cấu hình cỡ chữ nhỏ gọn theo yêu cầu trước đó
        if is_vertical:
            size_title = "55px"
            size_desc = "16px"
            size_tag = "14px"
            pos_left = "30px"
            width_content = "80%"
        else:
            size_title = "85px"
            size_desc = "20px"
            size_tag = "16px"
            pos_left = "80px"
            width_content = "750px"

        dynamic_style = f'''
            .container {{ width: 100vw; height: 100vh; {"max-width: 600px; margin: auto;" if is_vertical else ""} position: relative; }}
            .item {{ width: 100%; height: 100%; position: absolute; top: 0; left: 0; display: none; overflow: hidden; }}
            .item:first-child {{ display: block; }}
            .video-bg {{ width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; }}
            .video-bg video, .video-bg iframe {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
            {" .video-bg iframe { width: 300%; left: -100%; } " if not is_vertical else ""}

            .content {{ 
                position: absolute; 
                top: 50%; 
                left: {pos_left}; 
                transform: translateY(-50%); 
                color: #fff; 
                z-index: 10; 
                width: {width_content}; 
                padding: 40px;
                border-radius: 25px;
                background: rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .name {{ 
                font-family: 'Montserrat'; 
                font-size: {size_title}; 
                font-weight: 900; 
                text-transform: uppercase; 
                padding-left: 25px; 
                line-height: 1.0;
                text-shadow: 5px 5px 20px rgba(0,0,0,0.8);
            }}
            .des {{ 
                font-size: {size_desc}; 
                margin-top: 25px; 
                text-shadow: 2px 2px 10px #000; 
                line-height: 1.5;
                font-weight: 400;
                color: #e0e0e0;
                letter-spacing: 0.5px;
            }}
            .tag {{ 
                display: inline-block; 
                padding: 6px 20px; 
                border-radius: 50px; 
                color: #000; 
                font-weight: 800; 
                margin-bottom: 20px; 
                text-transform: uppercase; 
                font-size: {size_tag};
                letter-spacing: 1px;
            }}
        '''

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Open+Sans:wght@400;600;800&display=swap" rel="stylesheet">
            <style>
                body {{ margin: 0; background: #000; font-family: 'Open Sans', sans-serif; }}
                {dynamic_style}
                .overlay {{ 
                    position: absolute; 
                    top: 0; 
                    left: 0; 
                    width: 100%; 
                    height: 100%; 
                    background: linear-gradient(to right, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.7) 100%); 
                    z-index: 5; 
                }}
                .controls {{ position: absolute; bottom: 50px; width: 100%; text-align: center; z-index: 100; }}
                .controls button {{ width: 70px; height: 70px; border-radius: 50%; border: 2px solid #fff; background: rgba(0,0,0,0.5); color: #fff; font-size: 25px; cursor: pointer; margin: 0 15px; transition: 0.3s; }}
                .controls button:hover {{ background: orange; color: #000; border-color: orange; transform: scale(1.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="slide-wrapper">{items_html}</div>
                <div class="controls">
                    <button onclick="prev()">❮</button>
                    <button onclick="next()">❯</button>
                </div>
            </div>
            <script>
                let current = 0;
                let items = document.querySelectorAll('.item');
                function show(index) {{
                    items.forEach(it => it.style.display = 'none');
                    items[index].style.display = 'block';
                }}
                function next() {{ current = (current + 1) % items.length; show(current); }}
                function prev() {{ current = (current - 1 + items.length) % items.length; show(current); }}
            </script>
        </body>
        </html>'''

    def deploy(e):
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Fixed alignment and font adjustments"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            page.snack_bar = ft.SnackBar(ft.Text("Đã cập nhật website thành công!"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi: {ex}"))
            page.snack_bar.open = True
        page.update()

    page.add(
        ft.Column([
            ft.Container(content=ft.Text("VIDEO ANIMAL STUDIO 4K", size=40, weight="bold", font_family="Montserrat",
                                         color="orange"), alignment=ft.Alignment(0, 0)),
            format_selector,
            entries_container,
            ft.Row([
                ft.FilledButton("THÊM VIDEO", icon=ft.Icons.ADD, on_click=add_more),
                ft.FilledButton("CẬP NHẬT WEBSITE", icon=ft.Icons.UPLOAD, on_click=deploy, bgcolor="blue", width=400,
                                height=60)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)