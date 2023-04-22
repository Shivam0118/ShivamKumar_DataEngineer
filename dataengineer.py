import requests
import xml.etree.ElementTree as ET
import zipfile
import csv

url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-01T00:00:00Z+TO+2021-01-31T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"

response = requests.get(url)

doc = ET.fromstring(response.content)

zip_url = None
for str_tag in doc.findall(".//str"):
    if str_tag.attrib["name"] == "download_link" and "DLTINS" in str_tag.text:
        zip_url = str_tag.text
        break

if zip_url is None:
    print("No download link found for DLTINS file type")
    exit()

print("Downloading ZIP file from:", zip_url)

response = requests.get(zip_url)

with open("output.zip", "wb") as outfile:
    outfile.write(response.content)

print("Extracting XML file from ZIP")

with zipfile.ZipFile("output.zip", "r") as myzip:
    xml_filename = None
    for name in myzip.namelist():
        if "DLTINS" in name:
            xml_filename = name
            break

    if xml_filename is None:
        print("No XML file found in ZIP")
        exit()

    with myzip.open(xml_filename) as myfile:
        xml_content = myfile.read().decode("utf-8")

root = ET.fromstring(xml_content)

data = []
for instr in root.findall(".//FinInstrmGnlAttrbts"):
    instr_data = {}
    instr_data["FinInstrmGnlAttrbts.Id"] = instr.find("Id").text
    instr_data["FinInstrmGnlAttrbts.FullNm"] = instr.find("FullNm").text
    instr_data["FinInstrmGnlAttrbts.ClssfctnTp"] = instr.find("ClssfctnTp").text
    instr_data["FinInstrmGnlAttrbts.CmmdtyDerivInd"] = instr.find("CmmdtyDerivInd").text
    instr_data["FinInstrmGnlAttrbts.NtnlCcy"] = instr.find("NtnlCcy").text
    instr_data["Issr"] = instr.find("Issr").text
    data.append(instr_data)

if not data:
    print("No FinInstrmGnlAttrbts elements found in XML file")
    exit()

with open("output.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("CSV file generated successfully")
