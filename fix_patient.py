content = open('pages/patient.py', 'r', encoding='utf-8').read()
new_code = """
            c1, c2, c3 = st.columns([1,1,1.5])
            with c1:
                st.markdown("**Original Image**")
                st.image(img, use_container_width=True)
            with c2:
                st.markdown("**Processed Image**")
                st.image(proc, use_container_width=True)
            with c3:"""
content = content.replace('''            c1, c2 = st.columns([1,1])
            with c1:
                st.markdown("**Processed Image**")
                st.image(proc, use_container_width=True)
            with c2:''', new_code)
with open('pages/patient.py', 'w', encoding='utf-8') as f:
    f.write(content)
