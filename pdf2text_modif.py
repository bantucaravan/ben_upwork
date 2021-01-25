import six
import sys
import io
import pdfminer.settings
pdfminer.settings.STRICT = False
import pdfminer.high_level
import pdfminer.layout
from pdfminer.image import ImageWriter
#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.converter import TextConverter
#from pdfminer.pdfpage import PDFPage

def extract_text(files=[], outfile='-',
            _py2_no_more_posargs=None,  # Bloody Python2 needs a shim
            no_laparams=False, all_texts=None, detect_vertical=None, # LAParams
            word_margin=None, char_margin=None, line_margin=None, boxes_flow=None, # LAParams
            output_type='text', codec='utf-8', strip_control=False,
            maxpages=0, page_numbers=None, password="", scale=1.0, rotation=0,
            layoutmode='normal', output_dir=None, debug=False,
            disable_caching=False, **other):
    if _py2_no_more_posargs is not None:
        raise ValueError("Too many positional arguments passed.")
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin", "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    imagewriter = None
    if output_dir:
        imagewriter = ImageWriter(output_dir)

    if output_type == "text" and outfile != "-":
        for override, alttype in (  (".htm", "html"),
                                    (".html", "html"),
                                    (".xml", "xml"),
                                    (".tag", "tag") ):
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'
    
    if outfile == 'string_buffer':
        outfp = io.StringIO()

    else:
        outfp = open(outfile, "wb")

    assert len(files) == 1 # to emphasize my use case
    for fname in files:
        with open(fname, "rb") as fp:
            # old approach...
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
            
            '''
            # Alternative: selections from pdfminer.high_level.extract_text_to_fp 
            # source code
            imagewriter = None
            if output_dir:
                imagewriter = ImageWriter(output_dir)
        
            rsrcmgr = PDFResourceManager(caching=not disable_caching)

            if output_type == 'text':
                device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                                    imagewriter=imagewriter)

            if six.PY3 and outfp == sys.stdout:
                outfp = sys.stdout.buffer

            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp,
                                        page_numbers,
                                        maxpages=maxpages,
                                        password=password,
                                        caching=not disable_caching,
                                        check_extractable=True):
                page.rotate = (page.rotate + rotation) % 360
                interpreter.process_page(page)    
            # inspired by https://stackoverflow.com/questions/5725278/how-do-i-use-pdfminer-as-a-library
            
            #type(device) == pdfminer.converter.TextConverter
            device.close()
            ''' 

    if outfile == 'string_buffer': 
        str = outfp.getvalue() # returns string from io.StringIO
        return str

    return  # irrelevant closed string stream/buffer (if not string_buffer)
    #...already written to disk or printed to stdout
