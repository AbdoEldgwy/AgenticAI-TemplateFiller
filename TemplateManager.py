from docxtpl import DocxTemplate
from datetime import datetime


class ManageTemp():
    def __init__(self,temp_path,services) -> None:
        self.services = services
        self.doc = DocxTemplate(temp_path)

    def rendering(self, saved_path='outputs/filled_invoice.docx'):
        context = {
            "date": datetime.now().strftime("%d/%m/%Y") ,
            "services": self.services
    }
        self.doc.render(context)
        self.doc.save(saved_path)

        print("File saved ✅")

