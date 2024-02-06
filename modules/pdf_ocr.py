class OCRTool:
    SAVE_DIR = os.path.join('data', 'text')

    def __init__(self):
        if not os.path.exists(OCRTool.SAVE_DIR):
            os.makedirs(OCRTool.SAVE_DIR)
        self.model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                              extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
                                              label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})

    @staticmethod
    def load_pdf(file_name: str) -> Tuple[List, List]:
        """데이터 로드"""
        pdf_path = os.path.abspath(file_name)
        try:
            pdf_layout, pdf_images = lp.load_pdf(pdf_path, load_images=True,use_text_flow=True,dpi=144)
            return (pdf_layout, pdf_images)
        except FileNotFoundError as e:
            print(e)
    
    @staticmethod
    def save_data(data: str, file_name: str) -> None:
        """문자열을 텍스트 파일로 저장"""
        with open(os.path.join(OCRTool.SAVE_DIR, file_name), 'w') as file:
            file.write(data)

    def process_page(self, pdf_layout: List, pdf_images: List) -> List[dict]:
        """각 페이지의 텍스트 레이아웃을 처리하고 페이지 구조를 반환."""
        pages = []
        for pgn, layout in enumerate(tqdm(pdf_layout)):
            page = {}
            page['words'] = pd.DataFrame()
    
            pil_image = pdf_images[pgn].convert('RGB')
            image = np.array(pil_image)
            image = image[:, :, ::-1].copy()
            detected_layouts = self.model.detect(image)
    
            for i in layout:
                page['words'] = pd.concat([page['words'], pd.DataFrame([i.to_dict()])], ignore_index=True)
    
            for count, detected_layout in enumerate(detected_layouts):
                section_id = f'layout_{count+1}'
                section = {'layout': detected_layout, 'type': detected_layout.to_dict()['type'], 'words': pd.DataFrame()}
                page[section_id] = section
    
            for word in layout:
                for key in page.keys():
                    if 'layout' in key:
                        section = page[key]
                        if word.is_in(section['layout'], center=True):
                            dic = word.to_dict()
                            dic['section_type'] = section['type']
                            section['words'] = pd.concat([section['words'], pd.DataFrame([dic])], ignore_index=True)
    
            pages.append(page)
        return pages

    def extract_pdf_content(self, pages: List[dict]) -> str:
        """페이지 구조에서 PDF 콘텐츠를 추출하고 텍스트로 변환."""
        pdf_content_text = ''
        for page in tqdm(pages):
            for key in page.keys():
                if 'layout' in key:
                    section = page[key]
                    if section['type'] == 'Text' or section['type'] == 'Title':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        pdf_content_text += content + '\n'
                    elif section['type'] == 'Table':
                        content = ' '.join(section['words']['text']) if 'text' in section['words'] else ''
                        if '업종' in content:
                            pdf_content_text += "## 종목현황 ##\n" + content + '\n#### 닫음 : 종목현황 ####\n'
            
            # 페이지가 끝날 때마다 bar 붙임
            pdf_content_text += "\n==============================\n"
        return pdf_content_text


    def convert_to_text(self, pdf_layout: List, pdf_images: List) -> str:
        """PDF 이미지와 레이아웃을 활용하여 텍스트로 변환."""
        if len(pdf_layout) == 0 or len(pdf_images) == 0:
            raise Exception("변환할 파일이 존재하지 않습니다.")
        if len(pdf_layout) != len(pdf_images):
            raise Exception("페이지와 이미지 수가 일치하지 않습니다.")
            
        pages = self.process_page(pdf_layout, pdf_images)
        pdf_content_text = self.extract_pdf_content(pages)
        return pdf_content_text

# 예시 코드
if __name__ == "__main__":
    ocr = OCRTool();

    sample= "sample/232023베트남비즈니스팁.pdf" # 샘플 데이터
    sample_pdf_layout, sample_pdf_images = ocr.load_pdf(sample) # pdf load
    result = ocr.convert_to_text(sample_pdf_layout, sample_pdf_images) # convert
    ocr.save_data(result, "232023베트남비즈니스팁.txt") # save
