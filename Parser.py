from lxml import etree
import json
import os.path
import plotly.graph_objs as go

class Parser(object):

    def __init__(self, filename):

        if os.path.isfile(filename):
            self.filename = filename
        else:
             raise FileNotFoundError(filename)

    def parse(self):
        data = self.__convert(self.filename, self.__setup(self.filename))
        return data

    def __setup(self, filename):
        parser = etree.XMLParser(remove_comments=True)
        xmldoc = etree.parse(filename, parser = parser)
        root = xmldoc.getroot()
        return root

    def __convert(self, filename, root):
        datadictionary = {root.tag:
         {child.tag:
                {grandchild.tag:
                {attribute: self.__getname(attribute, grandchild) for attribute in grandchild.attrib}
            for grandchild in child

                }
             for child in root
            }
        }
        for child in root:
            for grandchild in child:
                if grandchild.text:
                    if "Detector" in grandchild.tag and any("type" in s for s in grandchild.attrib):
                        dimensions = grandchild.attrib["type"].replace("[", " ").replace(",", " ").replace("]", " ").split()
                        if len(dimensions) == 3 and dimensions[0] == "INT32":
                            dimensions.remove("INT32")
                            dimensions =[int(i) for i in dimensions]
                            cleaned_array = self.__arraysplit(grandchild.text.split(), dimensions)
                            datadictionary[root.tag][child.tag][grandchild.tag].update({"data" : cleaned_array})

                    else:
                        try:
                            datadictionary[root.tag][child.tag][grandchild.tag].update({"#text" : float(grandchild.text)})
                        except:
                            datadictionary[root.tag][child.tag][grandchild.tag].update({"#text" : grandchild.text})
        return datadictionary

    def __getname(self, attribute,child):
        try:
            return float(child.get(attribute))
        except:
            return child.get(attribute)


    def __arraysplit(self, data, dimensions):
        data = [int(i) for i in data]
        rows = dimensions[0]
        cols = dimensions[1]
        datalist = [data[x:x+cols] for x in range(0, len(data), cols)]
        return datalist


    def dump_as_dict(self):
        return self.parse()

    def dump_as_json(self):
        data =  self.parse()
        json_str= json.JSONEncoder().encode(data)
        return json_str

    def dump_to_file(self, output_file):
        data=  self.parse()
        with open(output_file, 'w') as f:
            json.dump(data, f)
        print("Dumped to %s" %(output_file))

    def xpath_get(self, path):

    #@path is the form of "/tag/tag/tag"
        elem = self.dump_as_dict()
        for x in path.strip("/").split("/"):
            elem = elem.get(x)
            if elem is None:
                raise TypeError("No results")
        return elem


def main():
    p = Parser("Data Examples/psBioSANS.xml")
    #print(p.dump_as_json())
    #print(p.dump_as_dict()["SPICErack"]["Counters"]["time"]["#text"])
    #print(p.xpath_get("/SPICErack/Counters/"))
    data = p.xpath_get("/SPICErack/Data/Detector/data")
    #print(data)

    import numpy as np
    from scipy import ndimage
    import matplotlib.pyplot as plt
    import plotly.offline as py

    data_array = np.array(data)

    com = ndimage.center_of_mass(data_array)
    com = [x for x in com]
    graph_data = [
    go.Contour(z = data_array)]
    layout = go.Layout(
    showlegend=False,
    annotations=[
        dict(
            x= com[0],
            y= com[1],
            xref='x',
            yref='y',
            text='Center',
            showarrow=True,
            font=dict(
                family='Courier New, monospace',
                size=10,
                color='#ffffff'
            ),
            align='center',
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#636363',
            ax=20,
            ay=-30,
            bordercolor='#c7c7c7',
            borderwidth=2,
            borderpad=4,
            bgcolor='#ff7f0e',
            opacity=0.8
        )
    ]
)
    fig = go.Figure(data=graph_data, layout=layout)
    plot_url = py.plot(fig, filename='text-chart-styling.html')
if __name__ == "__main__":
    main()
