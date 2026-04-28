import flet as ft
import os
import json
import subprocess

# Cấu hình Alignment cố định
ALIGN_CENTER = ft.Alignment(0, 0)


def main(page: ft.Page):
    # Cấu hình phông chữ
    page.fonts = {
        "Montserrat": "https://fonts.gstatic.com/s/montserrat/v25/JTUSjIg1_i6t8kCHKm459Wlhyw.ttf",
        "OpenSans": "https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf"
    }

    page.title = "Animal Photo Studio - Voice & Music Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1550
    page.window_height = 950
    page.padding = 25
    page.theme = ft.Theme(font_family="OpenSans")

    DATA_FILE = "data_studio.json"
    all_rows_data = []
    entries_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    # Ô nhập nhạc nền (mặc định lấy tên file bạn đã upload)
    bg_music_input = ft.TextField(
        label="Tên file nhạc nền (vd: Splashing Around - The Green Orbs.mp3)",
        value="Splashing Around - The Green Orbs.mp3",
        width=500,
        border_color="blue"
    )

    def save_data(e=None):
        data_to_save = {
            "format": format_selector.value,
            "bg_music": bg_music_input.value,
            "rows": []
        }
        for r in all_rows_data:
            data_to_save["rows"].append({
                "img": r["img"].value,
                "title": r["title"].value,
                "desc": r["desc"].value,
                "note": r["note"].value,
                "voice": r["voice"].value,
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

    def create_animal_row(img_val="", title_val="", desc_val="", note_val="", voice_val="Nữ", theme_val="Rừng",
                          label_val=""):
        # Tạo controls trước
        f1 = ft.TextField(label="File ảnh", width=120, value=img_val, border_color="orange")
        f2 = ft.TextField(label="Tiêu đề", width=180, value=title_val)
        f3 = ft.TextField(label="Giới thiệu", expand=True, value=desc_val)
        f4 = ft.TextField(label="Ghi chú", width=150, value=note_val)

        f_voice = ft.Dropdown(
            label="Giọng", width=90, value=voice_val,
            options=[ft.dropdown.Option("Nam"), ft.dropdown.Option("Nữ")]
        )

        f_label = ft.TextField(label="Nhãn", width=110, value=label_val if label_val else theme_val)

        f_theme = ft.Dropdown(
            label="Tông", width=100, value=theme_val,
            options=[ft.dropdown.Option("Rừng"), ft.dropdown.Option("Biển"), ft.dropdown.Option("Sa mạc"),
                     ft.dropdown.Option("Tuyết")]
        )

        # Gán sự kiện on_change sau để tránh lỗi version Flet
        f1.on_change = on_change_handler
        f2.on_change = on_change_handler
        f3.on_change = on_change_handler
        f4.on_change = on_change_handler
        f_voice.on_change = on_change_handler
        f_label.on_change = on_change_handler
        f_theme.on_change = on_change_handler

        row_content = ft.Row([
            f1, f2, f3, f4, f_voice, f_label, f_theme,
            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red400",
                          on_click=lambda _: remove_row(row_container))
        ])

        row_container = ft.Container(content=row_content, padding=12, border=ft.Border.all(1, ft.Colors.WHITE12),
                                     border_radius=12, bgcolor=ft.Colors.WHITE10)
        row_entry = {"img": f1, "title": f2, "desc": f3, "note": f4, "voice": f_voice, "label": f_label,
                     "theme": f_theme, "ui": row_container}
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
        value="horizontal"
    )
    format_selector.on_change = on_change_handler

    def load_saved_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                format_selector.value = data.get("format", "horizontal")
                bg_music_input.value = data.get("bg_music", "Splashing Around - The Green Orbs.mp3")
                for r_data in data.get("rows", []):
                    entries_container.controls.append(create_animal_row(
                        r_data.get("img", ""), r_data.get("title", ""),
                        r_data.get("desc", ""), r_data.get("note", ""),
                        r_data.get("voice", "Nữ"), r_data.get("theme", "Rừng"),
                        r_data.get("label", "")
                    ))
                return True
            except Exception:
                pass
        return False

    if not load_saved_data():
        for _ in range(2): entries_container.controls.append(create_animal_row())

    def generate_html_content():
        is_vertical = format_selector.value == "vertical"
        items_js = []
        theme_map = {"Rừng": "#4CAF50", "Biển": "#00BCD4", "Sa mạc": "#FFC107", "Tuyết": "#E0F7FA"}

        num_items = len(all_rows_data)

        for r in all_rows_data:
            if r["img"].value and r["title"].value:
                items_js.append({
                    "img": r["img"].value.strip(),
                    "title": r["title"].value.strip(),
                    "desc": r["desc"].value.strip(),
                    "note": r["note"].value.strip(),
                    "voice": r["voice"].value,
                    "label": r["label"].value.strip(),
                    "color": theme_map.get(r["theme"].value, "#ffffff")
                })

        # Cấu hình Thumbnail tự động co giãn thông minh
        if num_items <= 3:
            thumb_w, thumb_h = ("120px", "180px") if is_vertical else ("220px", "330px")
        elif num_items <= 6:
            thumb_w, thumb_h = ("90px", "140px") if is_vertical else ("160px", "240px")
        else:
            thumb_w, thumb_h = ("65px", "100px") if is_vertical else ("120px", "180px")

        size_title = "50px" if is_vertical else "80px"
        pos_left = "30px" if is_vertical else "80px"
        width_content = "85%" if is_vertical else "750px"

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ margin: 0; background: #000; font-family: 'Open Sans', sans-serif; overflow: hidden; }}
                .container {{ width: 100vw; height: 100vh; {"max-width: 600px; margin: auto;" if is_vertical else ""} position: relative; }}
                .item {{ position: absolute; width: 100%; height: 100%; background-size: cover; background-position: center; transition: 0.8s; display: none; }}
                .item.active {{ display: block; }}
                .overlay {{ position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(to right, rgba(0,0,0,0.85), transparent, rgba(0,0,0,0.85)); z-index: 5; }}

                .content {{ 
                    position: absolute; top: 50%; left: {pos_left}; transform: translateY(-50%); 
                    color: #fff; z-index: 100; width: {width_content}; padding: 40px;
                    border-radius: 25px; background: rgba(0,0,0,0.4); backdrop-filter: blur(15px);
                    border: 1px solid rgba(255,255,255,0.15); display: none;
                }}
                .item.active .content {{ display: block; animation: showContent 0.8s ease-out forwards; }}

                .name {{ font-family: 'Montserrat'; font-size: {size_title}; font-weight: 900; text-transform: uppercase; line-height: 1.1; margin-bottom: 20px; text-shadow: 5px 5px 20px #000; }}
                .des {{ font-size: 20px; color: #ddd; margin-bottom: 25px; line-height: 1.6; font-weight: 400; }}
                .note-box {{ font-family: 'Montserrat'; font-weight: 800; font-size: 32px; text-transform: uppercase; letter-spacing: 1px; }}

                /* THANH THUMBNAIL TỐI ƯU */
                .thumbnails {{ 
                    position: absolute; 
                    bottom: 50px; 
                    right: 50px; 
                    display: flex; 
                    gap: 15px; 
                    z-index: 110; 
                    justify-content: flex-end;
                    align-items: flex-end;
                }}
                .thumb {{ 
                    width: {thumb_w}; 
                    height: {thumb_h}; 
                    border-radius: 15px; 
                    background-size: cover; 
                    background-position: center; 
                    border: 2px solid rgba(255,255,255,0.2); 
                    transition: 0.5s; 
                    opacity: 0.5; 
                }}
                .thumb.active {{ opacity: 1; border-color: orange; transform: scale(1.05); box-shadow: 0 0 20px rgba(255,165,0,0.5); }}

                #start-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 999; display: flex; align-items: center; justify-content: center; }}
                #start-btn {{ padding: 25px 60px; font-family: 'Montserrat'; font-size: 26px; font-weight: 900; background: orange; color: #000; border: none; border-radius: 50px; cursor: pointer; transition: 0.3s; }}
                #start-btn:hover {{ transform: scale(1.1); background: #fff; }}

                @keyframes showContent {{ from {{ opacity: 0; transform: translate(-30px, -50%); }} to {{ opacity: 1; transform: translate(0, -50%); }} }}
            </style>
        </head>
        <body>
            <div id="start-overlay"><button id="start-btn">BẮT ĐẦU TRẢI NGHIỆM</button></div>
            <audio id="bg-music" loop src="assets/{bg_music_input.value}"></audio>

            <div class="container" id="main-slide"></div>
            <div class="thumbnails" id="thumb-bar"></div>

            <script>
                const data = {json.dumps(items_js)};
                let currentIndex = 0;
                const synth = window.speechSynthesis;
                const bgMusic = document.getElementById('bg-music');

                function init() {{
                    const slideCont = document.getElementById('main-slide');
                    const thumbCont = document.getElementById('thumb-bar');
                    data.forEach((item, i) => {{
                        const slide = document.createElement('div');
                        slide.className = `item ${{i===0?'active':''}}`;
                        slide.style.backgroundImage = `url('assets/${{item.img}}')`;
                        slide.innerHTML = `
                            <div class="overlay"></div>
                            <div class="content">
                                <div class="name" style="border-left: 12px solid ${{item.color}}; padding-left: 25px;">${{item.title}}</div>
                                <div class="des">${{item.desc}}</div>
                                <div class="note-box" style="color: ${{item.color}}; text-shadow: 0 0 15px ${{item.color}}80;">${{item.note}}</div>
                            </div>`;
                        slideCont.appendChild(slide);

                        const thumb = document.createElement('div');
                        thumb.className = `thumb ${{i===0?'active':''}}`;
                        thumb.style.backgroundImage = `url('assets/${{item.img}}')`;
                        thumbCont.appendChild(thumb);
                    }});
                }}

                function speak(item) {{
                    synth.cancel();
                    const textToRead = `${{item.title}}. ${{item.desc}}. ${{item.note}}`;
                    const utter = new SpeechSynthesisUtterance(textToRead);
                    utter.lang = 'vi-VN';
                    const voices = synth.getVoices();
                    const viVoices = voices.filter(v => v.lang.includes('vi'));

                    if (item.voice === 'Nam') {{
                        utter.voice = viVoices.find(v => v.name.includes('Male') || v.name.includes('An') || v.name.includes('Lê Minh')) || viVoices[0];
                    }} else {{
                        utter.voice = viVoices.find(v => v.name.includes('Female') || v.name.includes('Linh') || v.name.includes('Lan Nhi')) || viVoices[0];
                    }}

                    utter.rate = 0.92;
                    synth.speak(utter);

                    utter.onend = () => {{
                        setTimeout(nextSlide, 3500);
                    }};
                }}

                function nextSlide() {{
                    const slides = document.querySelectorAll('.item');
                    const thumbs = document.querySelectorAll('.thumb');
                    if (slides.length <= 1) return;

                    slides[currentIndex].classList.remove('active');
                    thumbs[currentIndex].classList.remove('active');

                    currentIndex = (currentIndex + 1) % data.length;

                    slides[currentIndex].classList.add('active');
                    thumbs[currentIndex].classList.add('active');
                    speak(data[currentIndex]);
                }}

                document.getElementById('start-btn').onclick = () => {{
                    document.getElementById('start-overlay').style.display = 'none';
                    bgMusic.volume = 0.25;
                    bgMusic.play().catch(e => console.log(e));
                    speak(data[0]);
                }};

                init();
                window.speechSynthesis.onvoiceschanged = () => {{}};
            </script>
        </body>
        </html>
        '''

    def deploy(e):
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Fixed dropdown error and thumbnail bar"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            page.snack_bar = ft.SnackBar(ft.Text("Đã sửa lỗi và cập nhật lên GitHub!"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi đồng bộ: {ex}"))
            page.snack_bar.open = True
        page.update()

    def preview_local(e):
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            os.startfile(os.path.abspath("index.html"))
        except:
            subprocess.run(["open", os.path.abspath("index.html")])

    page.add(
        ft.Column([
            ft.Container(content=ft.Text("ANIMAL STUDIO - AUTO VOICE & MUSIC", size=35, weight="bold", color="orange"),
                         alignment=ALIGN_CENTER),
            ft.Row([bg_music_input], alignment=ft.MainAxisAlignment.CENTER),
            format_selector,
            entries_container,
            ft.Row([
                ft.FilledButton("THÊM ẢNH", icon=ft.Icons.ADD_A_PHOTO, on_click=add_more),
                ft.FilledButton("XEM TRỰC TIẾP", icon=ft.Icons.PREVIEW, on_click=preview_local, bgcolor="green"),
                ft.FilledButton("ĐẨY LÊN GITHUB", icon=ft.Icons.UPLOAD, on_click=deploy, bgcolor="blue", width=350,
                                height=60)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)