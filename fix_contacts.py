import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix docstring header
content = content.replace(
    'Author: Gayathri0811 | PyTorch + Streamlit',
    'Mini Project | PyTorch + Streamlit'
)

# 2. Remove Contact from navbar
content = content.replace(
    '<a href="#">Contact</a>',
    ''
)

# 3. Remove FAQ contact section (the 3-column cards with email/github/huggingface)
# Find and remove the contact block in FAQ tab
old_faq_contact = '''    st.markdown("---")
    st.markdown(\'<div style="color:#74b9ff; font-size:1.1rem; font-weight:700; margin-bottom:1rem;">📬 Contact & Support</div>\',
                unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    for col, icon, title, detail in [
        (cc1, "📧", "Email",   "gayathriproject1108@gmail.com"),
        (cc2, "🐙", "GitHub",  "github.com/gayathri0811-git/retina-ai"),
        (cc3, "🌐", "Spaces",  "huggingface.co/spaces/gayathri0811-git/retina-ai"),
    ]:
        col.markdown(f"""
        <div class="feature-card" style="text-align:center;">
          <span class="feature-icon">{icon}</span>
          <div class="feature-title">{title}</div>
          <div class="feature-desc">{detail}</div>
        </div>""", unsafe_allow_html=True)'''

new_faq_contact = '''    st.markdown("---")
    st.markdown(\'<div style="color:#74b9ff; font-size:1.1rem; font-weight:700; margin-bottom:1rem;">📬 About This Project</div>\',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="info-panel" style="max-width:600px;">
      <h4>🎓 Mini Project</h4>
      <p style="color:#90a4ae; font-size:0.92rem; line-height:1.8;">
      This project was developed as an academic mini project demonstrating the application
      of deep learning in medical imaging. It showcases how AI can assist in early detection
      of Retinitis Pigmentosa using retinal fundus photography and convolutional neural networks.
      </p>
      <p style="color:#607d8b; font-size:0.85rem;">
      Stack: PyTorch · Streamlit · ResNet50 · ReportLab · Plotly
      </p>
    </div>
    """, unsafe_allow_html=True)'''

content = content.replace(old_faq_contact, new_faq_contact)

# 4. Fix footer - remove author name and links
content = content.replace(
    'gayathriproject1108@gmail.com',
    ''
)
content = content.replace(
    'github.com/gayathri0811-git/retina-ai',
    ''
)
content = content.replace(
    'huggingface.co/spaces/gayathri0811-git/retina-ai',
    ''
)
content = content.replace(
    '© {datetime.now().year} Retina AI · Built by Gayathri0811 · MIT License',
    '© {datetime.now().year} Retina AI · Mini Project · MIT License'
)
content = content.replace(
    'Built by Gayathri0811',
    'Mini Project'
)

# 5. Fix footer links - remove Contact
content = content.replace(
    '<a href="#">Home</a><a href="#">Analysis</a>\n        <a href="#">About RP</a><a href="#">Research</a><a href="#">FAQ</a>',
    '<a href="#">Home</a><a href="#">Analysis</a>\n        <a href="#">About RP</a><a href="#">Research</a><a href="#">FAQ</a>'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! All contact details removed.')
