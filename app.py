from flask import Flask, render_template, request, send_file, redirect, url_for
from utils import generate_pdf, generate_range
import io
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    mode = request.form.get('mode')
    items = [] # Will contain dicts: {'text': str, 'barcode': str}
    
    if mode == 'range':
        start_tag = request.form.get('start_tag')
        end_tag = request.form.get('end_tag')
        range_serials_raw = request.form.get('range_serials', '').strip()
        
        if start_tag and end_tag:
            generated_tags = generate_range(start_tag, end_tag)
            
            if range_serials_raw:
                # User provided specific serials for the range
                import re
                serials = [s.strip() for s in re.split(r'[\r\n]+', range_serials_raw) if s.strip()]
                
                # Zip them together.
                # If lengths mismatch, we zip as many as we can (or could error out).
                # For robustness, we'll try to match them up.
                for i, tag in enumerate(generated_tags):
                    barcode_val = serials[i] if i < len(serials) else tag # Fallback to tag if ran out of serials
                    items.append({'text': tag, 'barcode': barcode_val})
            else:
                # No separate serials, use tag for both
                items = [{'text': t, 'barcode': t} for t in generated_tags]
                
    elif mode == 'list':
        raw_list = request.form.get('tag_list')
        if raw_list:
            import re
            lines = [l.strip() for l in re.split(r'[\r\n]+', raw_list) if l.strip()]
            
            for line in lines:
                # Try to split by tab or comma for dual column
                # Regex split on comma or tab, max split 1
                parts = re.split(r'[\t,]', line, maxsplit=1)
                
                if len(parts) == 2:
                    text = parts[0].strip()
                    barcode = parts[1].strip()
                    items.append({'text': text, 'barcode': barcode})
                else:
                    text = line.strip()
                    items.append({'text': text, 'barcode': text})
            
    if not items:
        return "No tags generated. Please check your input.", 400
        
    pdf_buffer = generate_pdf(items)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='asset_tags.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
