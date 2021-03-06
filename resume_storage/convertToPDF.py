from models import Resume, Resume_Web, Saved_Section, Saved_Entry
from outline.models import Section, Entry, Data
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame
from reportlab.platypus import Paragraph, Table, Spacer, TableStyle
from reportlab.platypus import KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()


#this function will take the database entry from Resume, as resumeEntry
#and a file-like object, as outputFile
#and writes a pretty-ish looking resume into the file as a pdf
def writeResumePDF(resumeEntry, outputFile):
    doc = SimpleDocTemplate(outputFile, pagesize=letter)
    normalFrame = Frame(doc.leftMargin,
                        doc.rightMargin,
                        doc.width,
                        doc.height,
                        id='normal',)
    page = PageTemplate(frames=[normalFrame])
    doc.addPageTemplates([page, ])

    bulletStyle = ParagraphStyle(name='bulletStyle', leftIndent=0.25*inch)

    Document = []  # list of flowables for doc.build

    #begin with the resume's header data, piece-by-piece
    HeaderData = []
    for column in [resumeEntry.middle_initial(),
                   resumeEntry.email, ]:
        if column != '':
            HeaderData.append([column, []])
    for website in resumeEntry.resume_web_set.all():
        HeaderData.append([website.account, []])

    i = 0
    for column in [resumeEntry.cell,
                   resumeEntry.home,
                   resumeEntry.fax,
                   resumeEntry.address1,
                   resumeEntry.address2,
                   resumeEntry.region, ]:
        if column != '':
            if i == len(HeaderData):
                HeaderData.append(['', []])
            HeaderData[i][1] = column
            i += 1

    citstazip = ''
    if resumeEntry.city != '':
        citstazip += resumeEntry.city
    if resumeEntry.state != '':
        if citstazip != '':
            citstazip += ', '
        citstazip += resumeEntry.state
    if resumeEntry.zipcode != '':
        if citstazip != '':
            citstazip += ' '
        citstazip += resumeEntry.zipcode

    if citstazip != '':
        if i == len(HeaderData):
            HeaderData.append(['', []])
        HeaderData[i][1] = citstazip
        i += 1

    headerStyle = TableStyle([('ALIGN', (0, 0), (0, -1), 'LEFT'),
                              ('ALIGN', (1, 0), (1, -1), 'RIGHT'), ])
    Document.append(Table(HeaderData,
                          colWidths=[doc.width/2, doc.width/2],
                          style=headerStyle))

    #now for the sections, entries, and datums
    outline = resumeEntry.getResumeFields()
    for section in outline.keys():
        Document.append(KeepTogether([Paragraph(section.section.title,
                                                styles['Normal']),
                                      Paragraph(section.section.description,
                                                styles['Normal'])]))
        Document.append(Spacer(height=0.25*inch, width=1))
        for entry in outline[section].keys():
            entryHeader = []
            for item in [entry.entry.title, entry.entry.subtitle]:
                if item != '':
                    entryHeader.append([item, []])
            i = 0
            for item in [entry.date_string(0), entry.cityState()]:
                if i == len(entryHeader):
                    entryHeader.append(['', []])
                entryHeader[i][1] = item
                i += 1
            Document.append(Table(entryHeader,
                                  colWidths=[doc.width/2, doc.width/2],
                                  style=headerStyle))
            for item in [entry.entry.contact, entry.entry.description]:
                if item != '':
                    Document.append(Paragraph(item, bulletStyle))
            if entry.entry.display == 'L':
                for datum in entry.dataset.all():
                    Document.append(Paragraph(datum.text,
                                    bulletStyle))
            else:  # remaining option is display set to 'D' for delimited
                Document.append(Paragraph('\t'+entry.delimited(),
                                          styles['Normal']))
            Document.append(Spacer(height=0.25*inch, width=1))

    doc.build(Document)
    return outputFile
