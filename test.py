import popplerqt5
import sys
import PyQt5
import re



def annot_get_x(annotation,pwidth):
    quads = annotation.highlightQuads()
    for quad in quads:
        x = (quad.points[0].x() * pwidth)
    return x

def annot_get_y(annotation,pheight):
    quads = annotation.highlightQuads()
    for quad in quads:
        y = (quad.points[0].y() * pheight)
    return y

def main():
    dok = popplerqt5.Poppler.Document.load("/home/zelenyeshtany/Books/10StepstoEarningAwesomeGrades.pdf")
    paje = dok.page(28)
    pwidth = paje.pageSize().width()
    pheight = paje.pageSize().height()
    annots = paje.annotations()
    hlights = []
    if len(annots) > 0:
        for annotation in annots:
            if(isinstance(annotation, popplerqt5.Poppler.HighlightAnnotation)
               and
               (annotation.contents() == 'start'
                or
                annotation.contents() == 'end')
               ):
                hlights.append(annotation)
    print(len(hlights))
    # вывести коорды хайлайта
    print('hlight x' + str(annot_get_x(hlights[0],pwidth)))
    print('hlight y' + str(annot_get_y(hlights[0],pheight)))

    # вывести коорды слова
    for i in paje.textList():
        if('Note' in i.text()):
            textbox_under_hlight = i
    
    # сравнить коорды
    print('textbox x: ' + str(textbox_under_hlight.boundingBox().x()))
    print('textbox y: ' + str(textbox_under_hlight.boundingBox().y()))
if __name__ == "__main__":
    main()
