import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix titles
content = content.replace('page_title="AI Fake News Detector"', 'page_title="Fake AI"')
content = content.replace('Fake AI 🌐', 'Fake AI 🌐')

# Remove the broken markdown blocks
content = content.replace('st.markdown(\'<div class="glassmorphism">\', unsafe_allow_html=True)', '')
content = content.replace('st.markdown(\'<div class="glassmorphism" style="text-align:center;">\', unsafe_allow_html=True)', '')
content = content.replace('st.markdown(\'</div>\', unsafe_allow_html=True)', '')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed app.py")
