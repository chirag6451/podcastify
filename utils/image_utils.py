from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

def create_youtube_thumbnail(
    title: str,
    subtitle: str,
    background_image_path: str = "defaults/bgimages/bg2.jpeg",
    logo_image_path: str = "defaults/images/logo.jpg",
    output_path: str = "thumbnail_output.jpg",
    canvas_size: tuple = (1280, 720),
    title_font_path: str = "defaults/fonts/Roboto/static/Roboto_Condensed-Bold.ttf",
    subtitle_font_path: str = "defaults/fonts/Roboto/static/Roboto_Condensed-Italic.ttf",
    footer_font_path: str = "defaults/fonts/Roboto/static/Roboto_Condensed-MediumItalic.ttf",
    title_font_size: int = 120,
    subtitle_font_size: int = 80,
    footer_font_size: int = 30,
    title_font_color: str = "black",
    subtitle_font_color: str = "black",
    footer_font_color: str = "black",
    logo_scale: float = 0.10,
    logo_position: str = "top-right",
    logo_padding: int = 30,
    text_shadow: bool = True,
    text_shadow_color: str = "black",
    text_shadow_offset: tuple = (3, 3),
    vertical_spacing: int = 50,
    footer_text: str = None,
    footer_padding: int = 30
):
    """Creates a professional YouTube thumbnail using the provided images and text."""
    
    # Create base canvas
    canvas = Image.new('RGB', canvas_size, 'black')
    
    # Load and resize background image
    bg = Image.open(background_image_path).convert("RGB")
    bg = bg.resize(canvas_size, Image.Resampling.LANCZOS)
    canvas.paste(bg, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype(title_font_path, title_font_size)
        subtitle_font = ImageFont.truetype(subtitle_font_path, subtitle_font_size)
        footer_font = ImageFont.truetype(footer_font_path, footer_font_size)
    except Exception as e:
        print(f"Error loading fonts: {e}")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    # Calculate text sizes
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
    
    # Calculate total height for text placement
    total_height = title_height + vertical_spacing + subtitle_height
    start_y = (canvas_size[1] - total_height) // 2
    
    # Position text
    title_x = (canvas_size[0] - title_width) // 2
    title_y = start_y
    
    subtitle_x = (canvas_size[0] - subtitle_width) // 2
    subtitle_y = title_y + title_height + vertical_spacing
    
    # Draw text shadows if enabled
    if text_shadow:
        draw.text(
            (title_x + text_shadow_offset[0], title_y + text_shadow_offset[1]),
            title,
            font=title_font,
            fill=text_shadow_color
        )
        draw.text(
            (subtitle_x + text_shadow_offset[0], subtitle_y + text_shadow_offset[1]),
            subtitle,
            font=subtitle_font,
            fill=text_shadow_color
        )
    
    # Draw main text
    draw.text((title_x, title_y), title, font=title_font, fill=title_font_color)
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=subtitle_font_color)
    
    # Add logo if provided
    if logo_image_path and os.path.exists(logo_image_path):
        try:
            logo = Image.open(logo_image_path)
            # Calculate logo size based on canvas width
            logo_width = int(canvas_size[0] * logo_scale)
            logo_height = int(logo_width * (logo.size[1] / logo.size[0]))  # Maintain aspect ratio
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # Position logo
            if logo_position == "top-left":
                logo_x = logo_padding
                logo_y = logo_padding
            else:  # top-right
                logo_x = canvas_size[0] - logo_width - logo_padding
                logo_y = logo_padding
            
            # Add logo with transparency if available
            if logo.mode == 'RGBA':
                canvas.paste(logo, (logo_x, logo_y), logo)
            else:
                canvas.paste(logo, (logo_x, logo_y))
        except Exception as e:
            print(f"Error processing logo: {e}")
    
    # Simple footer text without effects
    if footer_text:
        footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_height = footer_bbox[3] - footer_bbox[1]
        footer_x = (canvas_size[0] - footer_width) // 2
        footer_y = canvas_size[1] - footer_height - footer_padding
        draw.text((footer_x, footer_y), footer_text, font=footer_font, fill=footer_font_color)
    
    # Save the final thumbnail
    canvas.save(output_path, quality=95, optimize=True)
    return output_path

# Example usage:
if __name__ == "__main__":
    bg_path = "defaults/bgimages/bg2.jpeg"  # replace with your background image path
    logo_path = "defaults/images/logo.jpg"      # replace with your logo image path
    title_font_path = "defaults/fonts/Roboto/static/Roboto_Condensed-Bold.ttf"
    subtitle_font_path = "defaults/fonts/Roboto/static/Roboto_Condensed-Italic.ttf"
    footer_font_path = "defaults/fonts/Roboto/static/Roboto_Condensed-MediumItalic.ttf"
    
    title = "How to Create YouTube Thumbnails and Videos "
    subtitle = "Step-by-step tutorial and you also need to know about YouTube"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create thumbnails directory if it doesn't exist
    os.makedirs("thumbnails", exist_ok=True)
    
    thumbnail_path = create_youtube_thumbnail(
        background_image_path=bg_path,
        logo_image_path=logo_path,
        title=title,
        subtitle=subtitle,
        title_font_path=title_font_path,
        subtitle_font_path=subtitle_font_path,
        footer_font_path=footer_font_path,
        title_font_size=80,
        subtitle_font_size=60,
        footer_font_size=30,
        title_font_color="white",
        subtitle_font_color="white",
        footer_font_color="white",
        logo_position="top-right",
        logo_scale=0.08,
        logo_padding=50,
        text_shadow=True,
        text_shadow_color="black",
        text_shadow_offset=(5, 5),
        vertical_spacing=80,
        footer_text="Visit www.example.com for more tutorials",
        footer_padding=40,
        output_path=f"thumbnails/{timestamp}_thumbnail.jpg"
    )

    print("Thumbnail created successfully on path:", thumbnail_path)