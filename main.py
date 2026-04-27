import flet as ft
import os
import json
import subprocess


def main(page: ft.Page):
    # Cấu hình phông chữ Google Fonts chuyên nghiệp
    page.fonts = {
        "Montserrat": "https://fonts.gstatic.com/s/montserrat/v25/JTUSjIg1_i6t8kCHKm459Wlhyw.ttf",
        "OpenSans": "https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf"
    }

    page.title = "Animal Studio - 4K Cinematic Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1450
    page.window_height = 950
    page.padding = 25
    page.theme = ft.Theme(font_family="OpenSans")

    DATA_FILE = "data_studio.json"
    all_rows_data = []

    # Khu vực danh sách có thể cuộn
    entries_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def save_data(e=None):
        data_to_save = {
            "format": format_selector.value,
            "rows": []
        }
        for r in all_rows_data:
            data_to_save["rows"].append({
                "img": r["img"].value,
                "title": r["title"].value,
                "desc": r["desc"].value,
                "note": r["note"].value,
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

    def create_animal_row(img_val="", title_val="", desc_val="", note_val="", theme_val="Rừng", label_val=""):
        f1 = ft.TextField(label="File ảnh", width=130, value=img_val, on_change=on_change_handler,
                          border_color="orange")
        f2 = ft.TextField(label="Tiêu đề", width=180, value=title_val, on_change=on_change_handler)
        f3 = ft.TextField(label="Giới thiệu", expand=True, value=desc_val, on_change=on_change_handler)
        f4 = ft.TextField(label="Ghi chú", width=130, value=note_val, on_change=on_change_handler)

        f_label = ft.TextField(
            label="Nhãn hiển thị",
            width=150,
            value=label_val if label_val else theme_val,
            on_change=on_change_handler,
            hint_text="VD: JUNGLE"
        )

        f_theme = ft.Dropdown(
            label="Màu/Môi trường",
            width=130,
            value=theme_val,
            options=[
                ft.dropdown.Option("Rừng"),
                ft.dropdown.Option("Biển"),
                ft.dropdown.Option("Sa mạc"),
                ft.dropdown.Option("Tuyết"),
                ft.dropdown.Option("Núi lửa"),
            ]
        )
        f_theme.on_change = on_change_handler

        row_content = ft.Row([
            f1, f2, f3, f4, f_label, f_theme,
            ft.IconButton(
                icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                icon_color="red400",
                on_click=lambda _: remove_row(row_container)
            )
        ])

        row_container = ft.Container(
            content=row_content,
            padding=15,
            border=ft.Border.all(1, ft.Colors.WHITE12),
            border_radius=12,
            bgcolor=ft.Colors.WHITE10
        )

        row_entry = {
            "img": f1, "title": f2, "desc": f3,
            "note": f4, "label": f_label, "theme": f_theme,
            "ui": row_container
        }
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
        entries_container.controls.append(create_animal_row())
        save_data()
        page.update()

    format_selector = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="horizontal", label="🎬 Ngang (4K)"),
            ft.Radio(value="vertical", label="📱 Dọc (TikTok)"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
        value="horizontal",
        on_change=on_change_handler
    )

    def load_saved_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                format_selector.value = data.get("format", "horizontal")
                saved_rows = data.get("rows", [])
                if saved_rows:
                    for r_data in saved_rows:
                        entries_container.controls.append(
                            create_animal_row(
                                r_data.get("img", ""),
                                r_data.get("title", ""),
                                r_data.get("desc", ""),
                                r_data.get("note", ""),
                                r_data.get("theme", "Rừng"),
                                r_data.get("label", "")
                            )
                        )
                    return True
            except Exception:
                pass
        return False

    if not load_saved_data():
        for _ in range(3):
            entries_container.controls.append(create_animal_row())

    def generate_html_content():
        is_vertical = format_selector.value == "vertical"
        items_html = ""
        count = 0

        theme_map = {
            "Rừng": "#4CAF50", "Biển": "#00BCD4", "Sa mạc": "#FFC107",
            "Tuyết": "#E0F7FA", "Núi lửa": "#FF5722"
        }

        for r in all_rows_data:
            img, title = r["img"].value.strip(), r["title"].value.strip()
            desc, note = r["desc"].value.strip(), r["note"].value.strip()
            custom_label = r["label"].value.strip()
            theme_name = r["theme"].value
            accent_color = theme_map.get(theme_name, "#ffffff")

            tag_html = f'<div class="theme-tag" style="background: {accent_color};">{custom_label}</div>' if custom_label else ''

            if img and title:
                count += 1
                items_html += f'''
                <div class="item" style="background-image: url('assets/{img}');">
                    <div class="overlay"></div>
                    <div class="content">
                        {tag_html}
                        <div class="name" style="border-left: 12px solid {accent_color};">{title}</div>
                        <div class="des">{desc}</div>
                        <div class="note-box" style="color: {accent_color}; text-shadow: 0 0 20px {accent_color};">{note}</div>
                    </div>
                </div>'''

        if count == 1:
            items_html += items_html + items_html
        elif count == 2:
            items_html += items_html

        dynamic_style = f'''
            .container {{ width: 100vw; height: 100vh; {"max-width: 650px; margin: auto;" if is_vertical else ""} }}
            .slide .item {{ width: {"220px; height: 350px;" if is_vertical else "300px; height: 450px;"} top: 82%; }}
            .item .content {{ left: {"30px; width: 85%; top: 60%;" if is_vertical else "100px; width: 900px; top: 50%;"} padding: 50px; }}
            .name {{ font-size: {"80px;" if is_vertical else "130px;"} }}
        '''

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Animal Studio Cinema</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ margin:0; background:#000; overflow:hidden; font-family: 'Open Sans', sans-serif; }}
                {dynamic_style}
                .container {{ position: relative; }}
                .slide .item {{ position: absolute; transform: translate(0, -50%); border-radius: 40px; background-size: cover; background-position: center; transition: 0.8s; box-shadow: 0 60px 100px rgba(0,0,0,0.95); }}
                .slide .item:nth-child(1), .slide .item:nth-child(2) {{ top:0; left:0; transform:translate(0,0); border-radius:0; width:100%; height:100%; }}
                .slide .item:nth-child(3) {{ left: {"50%;" if is_vertical else "60%;"} }}
                .slide .item:nth-child(4) {{ left: {"calc(50% + 250px);" if is_vertical else "calc(60% + 330px);"} }}
                .slide .item:nth-child(5) {{ left: calc(60% + 660px); }}
                .slide .item:nth-child(n+6) {{ opacity: 0; }}
                .overlay {{ position: absolute; width: 100%; height: 100%; background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.9) 100%); z-index: 1; }}
                .item .content {{ position: absolute; color: #fff; transform: translate(0, -50%); display: none; z-index: 99; border-radius: 40px; backdrop-filter: blur(20px); background: rgba(0,0,0,0.4); border: 2px solid rgba(255,255,255,0.2); }}
                .slide .item:nth-child(2) .content {{ display: block; animation: showContent 0.9s ease-out 1 forwards; }}
                .theme-tag {{ display: inline-block; padding: 8px 30px; border-radius: 50px; font-weight: bold; margin-bottom: 30px; font-family: 'Montserrat'; text-transform: uppercase; color: #000; font-size: 16px; letter-spacing: 2px; }}
                @keyframes showContent {{ from {{ opacity: 0; transform: translate(0, 100px); filter: blur(40px); }} to {{ opacity: 1; transform: translate(0, 0); filter: blur(0); }} }}
                .name {{ font-family: 'Montserrat', sans-serif; font-weight: 900; text-transform: uppercase; margin: 0; padding-left: 35px; line-height: 0.85; text-shadow: 15px 15px 50px rgba(0,0,0,1); }}
                .des {{ margin: 40px 0; line-height: 1.4; color: #fff; font-weight: 400; text-shadow: 4px 4px 25px rgba(0,0,0,1); }}
                .note-box {{ font-weight: 900; font-size: 40px; font-family: 'Montserrat', sans-serif; text-transform: uppercase; letter-spacing: 4px; }}
                .btn {{ position: absolute; bottom: 50px; width: 100%; text-align: center; z-index: 1000; }}
                .btn button {{ width: 100px; height: 100px; cursor: pointer; border-radius: 50%; border: 4px solid #fff; background: rgba(0,0,0,0.7); color: white; font-size: 45px; margin: 0 30px; transition: 0.4s; }}
                .btn button:hover {{ background: orange; border-color: orange; color: #000; transform: scale(1.2); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="slide">{items_html}</div>
                <div class="btn"><button class="prev">❮</button><button class="next">❯</button></div>
            </div>
            <script>
                document.querySelector('.next').onclick = () => {{
                    let items = document.querySelectorAll('.item');
                    if(items.length > 1) document.querySelector('.slide').appendChild(items[0]);
                }}
                document.querySelector('.prev').onclick = () => {{
                    let items = document.querySelectorAll('.item');
                    if(items.length > 1) document.querySelector('.slide').prepend(items[items.length - 1]);
                }}
            </script>
        </body>
        </html>'''

    def export_to_html(e):
        save_data()
        html_content = generate_html_content()
        path = os.path.abspath("review_video.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        os.startfile(path)

    def deploy_to_github(e):
        """Hàm tự động đổi tên file sang index.html và push lên GitHub"""
        save_data()
        html_content = generate_html_content()

        # 1. Tạo file index.html (Chuẩn cho GitHub Pages)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        try:
            # 2. Chạy các lệnh Git tự động
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update Animal Studio content"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)

            # Thông báo thành công (Dùng Banner hoặc Text đơn giản)
            page.snack_bar = ft.SnackBar(ft.Text("Đã đẩy lên GitHub thành công! Hãy đợi 1-2 phút để web cập nhật."))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi khi push: {ex} (Hãy chắc chắn bạn đã cài Git và Remote)"))
            page.snack_bar.open = True

        page.update()

    # Bố cục UI tổng thể
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("ANIMAL SERIES", size=50, weight="bold", font_family="Montserrat",
                            color=ft.Colors.ORANGE_400),
                    ft.Text("STUDIO 4K", size=50, weight="w100", font_family="Montserrat")
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=ft.Padding(0, 0, 0, 10)
            ),
            ft.Container(content=format_selector, padding=10),
            ft.Divider(height=10, color=ft.Colors.WHITE10),

            entries_container,

            ft.Divider(height=10, color=ft.Colors.WHITE10),

            ft.Row([
                ft.FilledButton("THÊM DÒNG MỚI", icon=ft.Icons.ADD_LOCATION_ALT_OUTLINED, on_click=add_more, height=55),
                ft.FilledButton(
                    "XEM TRỰC TIẾP",
                    icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                    on_click=export_to_html,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.BLACK,
                                         shape=ft.RoundedRectangleBorder(radius=15)),
                    width=300, height=80
                ),
                ft.FilledButton(
                    "ĐẨY LÊN GITHUB",
                    icon=ft.Icons.CLOUD_UPLOAD_OUTLINED,
                    on_click=deploy_to_github,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE,
                                         shape=ft.RoundedRectangleBorder(radius=15)),
                    width=300, height=80
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Container(
                content=ft.Text(f"Dữ liệu được bảo vệ tự động tại: {DATA_FILE}", color="white30", size=13, italic=True),
                alignment=ft.Alignment(0, 0)
            )
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)