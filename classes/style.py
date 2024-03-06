class CustomCSS:
    @staticmethod
    def get_button_styles():
        return """
        <style>
            .stButton > button {
                border: 1px solid #4f8bf9;
                color: #fff;
                background-color: #4f8bf9;
                border-radius: 20px;
                padding: 5px 20px;
                font-size: 14px;
            }

            .stButton > button:hover {
                border-color: #367be5;
                background-color: #367be5;
            }
        </style>
        """