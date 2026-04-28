import flet as ft
import os
import json
import subprocess

# Sử dụng class Alignment cố định để tránh lỗi version Flet trên các máy khác nhau
ALIGN_CENTER = ft.Alignment(0, 0)


def main(page: ft.Page):
    # Cấu hình phông chữ chuyên nghiệp từ Google Fonts
    page.fonts = {
        "Montserrat": "https://fonts.gstatic.com/s/montserrat/v25/JTUSjIg1_i6t8kCHKm459Wlhyw.ttf",
        "OpenSans": "https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf"
    }

    # Thiết lập trang
    page.title = "Animal Photo Studio - 4K Stable Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1450
    page.window_height = 950
    page.padding = 25
    page.theme = ft.Theme(font_family="OpenSans")

    # File lưu trữ dữ liệu ảnh
    DATA_FILE = "data_studio.json"
    all_rows_data = []

    # Container danh sách hàng nhập liệu có thanh cuộn
    entries_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def save_data(e=None):
        """Lưu toàn bộ dữ liệu vào file JSON"""
        data_to_save = {
            "format": format_selector.value,
            "rows": []
        }
        for r in all_rows_data:
            data_to_save["rows"].append({
                "img": r["img"].value,
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

    def create_animal_row(img_val="", title_val="", desc_val="", theme_val="Rừng", label_val=""):
        """Tạo một hàng nhập liệu cho ảnh"""
        f1 = ft.TextField(
            label="Tên file ảnh (vd: 1.jpg)",
            width=180,
            value=img_val,
            on_change=on_change_handler,
            border_color="orange"
        )
        f2 = ft.TextField(label="Tiêu đề", width=200, value=title_val, on_change=on_change_handler)
        f3 = ft.TextField(label="Giới thiệu", expand=True, value=desc_val, on_change=on_change_handler)
        f_label = ft.TextField(label="Nhãn (Vùng đất)", width=150, value=label_val if label_val else theme_val,
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

        row_container = ft.Container(
            content=row_content,
            padding=15,
            border=ft.Border.all(1, ft.Colors.WHITE12),
            border_radius=12,
            bgcolor=ft.Colors.WHITE10
        )
        row_entry = {"img": f1, "title": f2, "desc": f3, "label": f_label, "theme": f_theme, "ui": row_container}
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
                        create_animal_row(
                            r_data.get("img", ""),
                            r_data.get("title", ""),
                            r_data.get("desc", ""),
                            r_data.get("theme", "Rừng"),
                            r_data.get("label", "")
                        )
                    )
                return True
            except Exception:
                pass
        return False

    if not load_saved_data():
        for _ in range(2): entries_container.controls.append(create_animal_row())

    def generate_html_content():
        is_vertical = format_selector.value == "vertical"
        items_html = ""
        theme_map = {"Rừng": "#4CAF50", "Biển": "#00BCD4", "Sa mạc": "#FFC107", "Tuyết": "#E0F7FA",
                     "Núi lửa": "#FF5722"}

        for r in all_rows_data:
            img, title = r["img"].value.strip(), r["title"].value.strip()
            desc, label = r["desc"].value.strip(), r["label"].value.strip()
            color = theme_map.get(r["theme"].value, "#ffffff")

            if img and title:
                items_html += f'''
                <div class="item" style="background-image: url('assets/{img}');">
                    <div class="overlay"></div>
                    <div class="content">
                        {f'<div class="tag" style="background:{color}">{label}</div>' if label else ''}
                        <div class="name" style="border-left:10px solid {color}">{title}</div>
                        <div class="des">{desc}</div>
                    </div>
                </div>'''

        # Cỡ chữ nhỏ gọn (đã tối ưu để không che ảnh)
        if is_vertical:
            size_title, size_desc, size_tag = "50px", "16px", "14px"
            pos_left, width_content = "30px", "80%"
        else:
            size_title, size_desc, size_tag = "85px", "20px", "16px"
            pos_left, width_content = "80px", "700px"

        dynamic_style = f'''
            .container {{ width: 100vw; height: 100vh; {"max-width: 600px; margin: auto;" if is_vertical else ""} position: relative; }}
            .slide .item {{ position: absolute; transform: translate(0, -50%); border-radius: 40px; background-size: cover; background-position: center; transition: 0.8s; box-shadow: 0 60px 100px rgba(0,0,0,0.95); }}
            .slide .item:nth-child(1), .slide .item:nth-child(2) {{ top:0; left:0; transform:translate(0,0); border-radius:0; width:100%; height:100%; }}
            .slide .item:nth-child(3) {{ left: {"50%;" if is_vertical else "60%;"} }}
            .slide .item:nth-child(4) {{ left: {"calc(50% + 250px);" if is_vertical else "calc(60% + 330px);"} }}
            .slide .item:nth-child(5) {{ left: calc(60% + 660px); }}
            .slide .item:nth-child(n+6) {{ opacity: 0; }}

            .content {{ 
                position: absolute; top: 50%; left: {pos_left}; transform: translateY(-50%); 
                color: #fff; z-index: 99; width: {width_content}; padding: 35px;
                border-radius: 20px; background: rgba(0,0,0,0.35); backdrop-filter: blur(12px);
                border: 1px solid rgba(255,255,255,0.15); display: none;
            }}
            .slide .item:nth-child(2) .content {{ display: block; animation: showContent 0.8s ease-out 1 forwards; }}

            .name {{ font-family: 'Montserrat'; font-size: {size_title}; font-weight: 900; text-transform: uppercase; padding-left: 20px; line-height: 1.1; text-shadow: 5px 5px 20px rgba(0,0,0,1); }}
            .des {{ font-size: {size_desc}; margin-top: 20px; line-height: 1.5; color: #eee; font-weight: 400; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 5px; color: #000; font-weight: 800; margin-bottom: 15px; text-transform: uppercase; font-size: {size_tag}; }}

            @keyframes showContent {{ from {{ opacity: 0; transform: translate(0, 50px); filter: blur(20px); }} to {{ opacity: 1; transform: translate(0, 0); filter: blur(0); }} }}
        '''

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ margin: 0; background: #000; font-family: 'Open Sans', sans-serif; overflow: hidden; }}
                {dynamic_style}
                .overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to right, rgba(0,0,0,0.8), transparent, rgba(0,0,0,0.8)); z-index: 5; }}
                .controls {{ position: absolute; bottom: 50px; width: 100%; text-align: center; z-index: 100; }}
                .controls button {{ width: 60px; height: 60px; border-radius: 50%; border: 2px solid #fff; background: rgba(0,0,0,0.4); color: #fff; font-size: 20px; cursor: pointer; margin: 0 15px; transition: 0.3s; }}
                .controls button:hover {{ background: orange; color: #000; border-color: orange; transform: scale(1.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="slide">{items_html}</div>
                <div class="controls">
                    <button class="prev">❮</button>
                    <button class="next">❯</button>
                </div>
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

    def preview_local(e):
        """Tạo file index.html và mở trình duyệt để xem trước tại máy"""
        save_data()
        html_content = generate_html_content()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        path = os.path.abspath("index.html")
        try:
            # Mở file index.html bằng trình duyệt mặc định
            os.startfile(path)
        except AttributeError:
            # Dành cho macOS/Linux nếu cần
            subprocess.run(["open", path])

        page.snack_bar = ft.SnackBar(ft.Text("Đang mở bản xem trước trên trình duyệt..."))
        page.snack_bar.open = True
        page.update()

    def deploy(e):
        """Đẩy dữ liệu lên GitHub"""
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Manual update from Studio"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            page.snack_bar = ft.SnackBar(ft.Text("Đã cập nhật lên GitHub! Hãy đợi 1-2 phút để web đổi mới."))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi: {ex}"))
            page.snack_bar.open = True
        page.update()

    # Bố cục giao diện Tool
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text("ANIMAL PHOTO STUDIO 4K", size=35, weight="bold", font_family="Montserrat",
                                color="orange"),
                alignment=ALIGN_CENTER
            ),
            format_selector,
            entries_container,
            ft.Row([
                ft.FilledButton("THÊM ẢNH", icon=ft.Icons.ADD_A_PHOTO, on_click=add_more),
                ft.FilledButton(
                    "XEM TRỰC TIẾP",
                    icon=ft.Icons.PREVIEW,
                    on_click=preview_local,
                    bgcolor=ft.Colors.GREEN_700
                ),
                ft.FilledButton(
                    "ĐẨY LÊN GITHUB",
                    icon=ft.Icons.UPLOAD,
                    on_click=deploy,
                    bgcolor=ft.Colors.BLUE_700,
                    width=350,
                    height=60
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)