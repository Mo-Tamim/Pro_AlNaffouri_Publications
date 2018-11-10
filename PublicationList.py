
import json
from datetime import datetime
import csv
import os
import difflib as diff
import re


class PublicationList2:
    def __init__(self, json_name, csv_name, bib_name):
        self.json_name = json_name
        self.csv_name = csv_name
        self.bib_name = bib_name
        self.bib_data = self.read_bib_file()

    def seperating_author_names(self, names):
        seperated_names = names.strip().split(' and ')
        if len(seperated_names) <= 1:
            seperated_names = names.strip().split(', ')
        author_names = ''
        for i_name in range(0, len(seperated_names)):
            if seperated_names[i_name].count('ffouri') > 0:
                #seperated_names[i_name] = "{\\bf " + seperated_names[i_name].strip() + '}'
                seperated_names[i_name] = '{\\bf T. Y. Al-Naffouri}'
            if i_name == len(seperated_names) - 1 and len(seperated_names) > 1:
                author_names = author_names + 'and ' + seperated_names[i_name].strip() + ','
            else:
                author_names = author_names + seperated_names[i_name].strip() + ', '
        return author_names



    def seperating_author_names_no_latex(self, names):
        seperated_names = names.strip().split(' and ')
        if len(seperated_names) <= 1:
            seperated_names = names.strip().split(', ')
        author_names = ''
        for i_name in range(0, len(seperated_names)):
            if seperated_names[i_name].count('ffouri') > 0:

                seperated_names[i_name] = ' T. Y. Al-Naffouri'
            if i_name == len(seperated_names) - 1 and len(seperated_names) > 1:
                author_names = author_names + 'and ' + seperated_names[i_name].strip() + ','
            else:
                author_names = author_names + seperated_names[i_name].strip() + ', '
        return author_names

    def read_bib_file(self):
        with open(self.bib_name, 'r', encoding="utf8") as bib_file:
            line1 = ''
            long_line = False
            bib_data = {}
            for line in bib_file:
                line = line.strip()
                # if '@' not in line and '=' not in line and '}' not in line:
                if '@' not in line and '}' not in line:
                    line1 += line
                    long_line = True
                    continue
                if long_line:
                    long_line = False
                    line = line1 + line
                    line1 = ''
                if '@' in line:
                    entry_key = line[line.index('{') + 1:]
                    entry_key = entry_key.replace(',', '')
                    bib_data[entry_key] = {}
                elif '=' in line and '}' in line and '@' not in line:
                    keyword_name = line[:line.index('=')].strip()
                    keyword_value = line[line.index('{') + 1: line.index('}')]
                    bib_data[entry_key][keyword_name] = keyword_value

        return bib_data
        # Save it to json file for future use

    @property
    def get_journals_list(self):
        journals_list = []
        for item_key in self.bib_data.keys():
            if 'journal' in self.bib_data[item_key].keys():
                journal_name = self.bib_data[item_key]['journal']
            elif 'booktitle' in self.bib_data[item_key].keys():
                journal_name = self.bib_data[item_key]['booktitle']
            else:
                journal_name = 'Unknown Journal'
                print('This journal in unknown =====' + item_key)

            if journal_name in journals_list:
                continue
            else:
                journals_list.append(journal_name)
        return journals_list

    def CreatingJsonFile(self):
        with open(self.json_name, 'w', encoding='utf8') as json_file:
            json.dump(self.bib_data, json_file, indent=2)

    @property
    def sort_by_date(self, publication_data = []):
        month_names_full = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']
        month_names_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_names = month_names_full + month_names_short
        if not publication_data:
            publication_data = self.bib_data

        # This loop is to check out the year and the status of the publications
        for item_key in publication_data:
            submitted_year = '2020'
            year_value = publication_data[item_key].get('year', submitted_year)
            if year_value == '':
                year_value = submitted_year
            publication_data[item_key].update({'year': year_value})
            if year_value == submitted_year:
                publication_data[item_key].update({'status': 'Submitted'})
            else:
                publication_data[item_key].update({'status': 'Published'})

        # This loop is to add date of publication for each entry
        for item_key in publication_data:
            month_name = publication_data[item_key].get('month', 'Feb')
            month_match = []
            for i_month in month_names_short:
                month_match.append(diff.SequenceMatcher(None,i_month.lower(), month_name[0:3].lower()).ratio()* 100)
            month_name = month_names_short[month_match.index(max(month_match))]

            publication_date_string = month_name + ' 01, ' + publication_data[item_key]['year']
            publication_data[item_key]['month'] = month_name
            publication_data[item_key]['PublicationDate'] = datetime.strptime(publication_date_string, '%b %d, %Y')

        short_sorted = []
        all_sorted_items = []


        # This loop is to generate a list of keyes associated with theiy publication date
        for item_key in publication_data:
            Temp = [item_key, publication_data[item_key]['PublicationDate']]
            short_sorted.append(Temp)
        sorted_keys = sorted(short_sorted, key=lambda t: t[1], reverse=True)
        formated_data = "{:%b, %Y}"


        # This loop add datetime object to each item in the dictionary
        for item_key0 in sorted_keys:
            item_key = item_key0[0]
            publication_date_formated = formated_data.format(publication_data[item_key]['PublicationDate'])
            if 'journal' in publication_data[item_key]:
                journal_name = publication_data[item_key]['journal']
            elif 'booktitle' in publication_data[item_key]:
                journal_name = publication_data[item_key]['booktitle']
            else:
                journal_name = ''
            author_names = self.seperating_author_names(publication_data[item_key]['author'])





            if publication_data[item_key]['status'].lower() == 'published':

                if publication_data[item_key].get('volume', '') != '':
                    publication_volum = ', vol.' + publication_data[item_key].get('volume')
                else:
                    publication_volum = ''
                if publication_data[item_key].get('pages', '') != '':
                    publication_page =  ', pp.' + publication_data[item_key]['pages']
                else:
                    publication_page = ''

                if "Conference" in self.bib_name:
                    full_entry = '\item ' + author_names + \
                                 ' ``' + publication_data[item_key]['title'] + \
                                 '", {\\em ' + journal_name + '}' +\
                                 publication_volum +\
                                 publication_page + \
                                 ', ' + publication_data[item_key]['month'] + \
                                 '. ' + publication_data[item_key]['year'] + '.'
                else:
                    full_entry = '\item ' + author_names + \
                                 ' ``' + publication_data[item_key]['title'] + \
                                 '", in {\\em ' + journal_name + '}' +\
                                 publication_volum +\
                                 publication_page + \
                                 ', ' + publication_data[item_key]['month'] + \
                                 '. ' + publication_data[item_key]['year'] + '.'

            else:
                full_entry = '\item ' + author_names + \
                             ' ``' + publication_data[item_key]['title'] + \
                             '", {\\em ' + journal_name + '}.'


            all_sorted_items.append(full_entry)
            self.all_sorted_items = all_sorted_items
        return all_sorted_items

# This function is to sort data according to date and put them in citation context without latex commands
    def sort_by_dat_no_Latex(self, publication_data = []):
        month_names_full = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']
        month_names_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_names = month_names_full + month_names_short
        if not publication_data:
            publication_data = self.bib_data

        # This loop is to check out the year and the status of the publications
        for item_key in publication_data:
            submitted_year = '2020'
            year_value = publication_data[item_key].get('year', submitted_year)
            if year_value == '':
                year_value = submitted_year
            publication_data[item_key].update({'year': year_value})
            if year_value == submitted_year:
                publication_data[item_key].update({'status': 'Submitted'})
            else:
                publication_data[item_key].update({'status': 'Published'})

        # This loop is to add date of publication for each entry
        for item_key in publication_data:
            month_name = publication_data[item_key].get('month', 'Feb')
            month_match = []
            for i_month in month_names_short:
                month_match.append(diff.SequenceMatcher(None,i_month.lower(), month_name[0:3].lower()).ratio()* 100)
            month_name = month_names_short[month_match.index(max(month_match))]

            publication_date_string = month_name + ' 01, ' + publication_data[item_key]['year']
            publication_data[item_key]['month'] = month_name
            publication_data[item_key]['PublicationDate'] = datetime.strptime(publication_date_string, '%b %d, %Y')

        short_sorted = []
        all_sorted_items = []


        # This loop is to generate a list of keyes associated with theiy publication date
        for item_key in publication_data:
            Temp = [item_key, publication_data[item_key]['PublicationDate']]
            short_sorted.append(Temp)
        sorted_keys = sorted(short_sorted, key=lambda t: t[1], reverse=True)
        formated_data = "{:%b, %Y}"


        # This loop add datetime object to each item in the dictionary
        for item_key0 in sorted_keys:
            item_key = item_key0[0]
            publication_date_formated = formated_data.format(publication_data[item_key]['PublicationDate'])
            if 'journal' in publication_data[item_key]:
                journal_name = publication_data[item_key]['journal']
            elif 'booktitle' in publication_data[item_key]:
                journal_name = publication_data[item_key]['booktitle']
            else:
                journal_name = ''
            author_names = self.seperating_author_names_no_latex(publication_data[item_key]['author'])





            if publication_data[item_key]['status'].lower() == 'published':

                if publication_data[item_key].get('volume', '') != '':
                    publication_volum = ', vol.' + publication_data[item_key].get('volume')
                else:
                    publication_volum = ''
                if publication_data[item_key].get('pages', '') != '':
                    publication_page =  ', pp.' + publication_data[item_key]['pages']
                else:
                    publication_page = ''

                if "Conference" in self.bib_name:
                    full_entry = author_names + \
                                 ' "' + publication_data[item_key]['title'] + \
                                 '", ' + journal_name + \
                                 publication_volum +\
                                 publication_page + \
                                 ', ' + publication_data[item_key]['month'] + \
                                 '. ' + publication_data[item_key]['year'] + '.'
                else:
                    full_entry =  author_names + \
                                 ' "' + publication_data[item_key]['title'] + \
                                 '", in ' + journal_name + \
                                 publication_volum +\
                                 publication_page + \
                                 ', ' + publication_data[item_key]['month'] + \
                                 '. ' + publication_data[item_key]['year'] + '.'

            else:
                full_entry = author_names + \
                             ' "' + publication_data[item_key]['title'] + \
                             '", ' + journal_name + '.'


            all_sorted_items.append(full_entry)
            self.all_sorted_items = all_sorted_items
        return all_sorted_items


    def writing_to_tex(self, tex_file_name='AllPub.txt'):
        with open(tex_file_name, 'w', encoding='utf8') as txt_file:
            for item in self.all_sorted_items:
                txt_file.write("%s\n" % item)
        txt_file.close()


    def CreateCSV(self):
        # pdb.set_trace()

        BIBKeys = [Key for Key in self.bib_data]
        CSVHeader = ["ItemKey"]
        for HeaderItem in self.bib_data[BIBKeys[1]]:
            CSVHeader.append(HeaderItem)


        with open('CSVTemp.csv', 'w', encoding='utf-8', newline='') as CSVFilePointer:
            CSVWriterPointer = csv.writer(CSVFilePointer)
            for BibKey in self.bib_data:
                CSVLineContent = []
                # This loop take an item from the CSV and put its value in the CSV line
                for HeaderItem in CSVHeader:
                    if HeaderItem == "ItemKey":
                        CSVLineContent.append(BibKey)
                        continue
                    if HeaderItem in self.bib_data[BibKey]:
                        CSVLineContent.append(self.bib_data[BibKey][HeaderItem])
                    else:
                        CSVLineContent.append('')

                # This loop search for a new head item an add it to the CSV head
                for HeaderItem in self.bib_data[BibKey]:
                    if HeaderItem not in CSVHeader:
                        CSVHeader.append(HeaderItem)
                        CSVLineContent.append(self.bib_data[BibKey][HeaderItem])

                CSVWriterPointer.writerow(CSVLineContent)

        # print(CSVFilePointer.closed)

        with open('CSVTemp.csv') as CSVFilePointer:
            CSVReaderPointer = csv.reader(CSVFilePointer)
            with open(self.csv_name, 'w+', newline='') as CSVFilePointer2:
                CSVWriterPointer = csv.writer(CSVFilePointer2)
                CSVWriterPointer.writerow(CSVHeader)
                for Row in CSVReaderPointer:
                    CSVWriterPointer.writerow(Row)
        os.remove('CSVTemp.csv')

#    def get_author_publications(self, author_name,bib_data):
#        for item_key in self.pub
def exctract_publication_by_name(publication_data, selected_author):
    selected_author_publication ={}
    for item_key in publication_data:
        if selected_author.lower() in publication_data[item_key]['author'].lower():
            selected_author_publication[item_key]=publication_data[item_key]
    return selected_author_publication




def main():


    journal_bib_name = "JournalPublications V6.bib"
    journal_json_name = 'JournalPublications V3.json'
    journal_csv_name = 'JournalPublications V3.csv'
    journal_publication_obj = PublicationList2(journal_json_name, journal_csv_name, journal_bib_name)
    journal_publication_data = journal_publication_obj.read_bib_file()
    all_sorted_pub = journal_publication_obj.sort_by_date
    journal_publication_obj.writing_to_tex('AllJournalPublications.txt')
    journal_publication_obj.CreateCSV()
    print('\n \n The total journal publications found for Professor Tareq is   ====> ' + str(len(journal_publication_data.keys())))





    print ('*************************************************************************************************************\n '
           '*************************************************************************************************************')






    # Selected Publication by name
    selected_author_list = ['Elkhalil', 'Eltayeb','Lin', 'AlSharif', 'Yao', 'Nahhas', 'Majeed', 'H. Ali', 'shah', 'Afify', 'Quadeer', 'A. Ali', 'Dahrouj', 'Alrashdi',
                            'Sohail', 'Chen', 'Dhifallah', 'Suliman', 'Masood', 'Alzuhair', 'Moubayed', 'Douik', 'M. F. A. Ahmed', 'Sorour', 'Bushnaq', 'Owodunni',
                            'Aljaloud', 'Niyazi', 'Almunif', 'Behzad', 'Zhapparov', 'Saeed', 'Alanazi', 'Alhindi', 'hujaili', 'Liu', 'Arshad', 'Shuhail',
                            'Zaib', 'Alkhodary', 'Shibli', 'S. Ahmed', 'Sana', 'Amri', 'Hussaini', 'Dahman', 'Emara', 'Saad', 'Saeed', 'Shnaiwer', 'Niyazi', 'Safadi', 'Ballal','Sorour']


    for selected_author in selected_author_list:
        selected_author_journal = exctract_publication_by_name(journal_publication_data, selected_author)
        journal_publication_obj.bib_data = selected_author_journal
        journal_publication_obj.sort_by_dat_no_Latex(selected_author_journal)
        journal_publication_obj.writing_to_tex('Student Publications\\' + selected_author + "_journals.txt")
        tex_file_name = 'Student Publications\\' + selected_author + "_journal_keys.txt"
        with open(tex_file_name, 'w', encoding='utf8') as txt_file:
            for item_key in selected_author_journal.keys():
                txt_file.write("%s\n" % item_key)
        txt_file.close()
        journal_publication_obj.all_sorted_items = []
        print('\n \n The total selected author journal publications found for ' + selected_author + ' is   ====> ' + str(len(selected_author_journal.keys())))


    print ('*************************************************************************************************************\n '
           '*************************************************************************************************************')


    conference_bib_name = "ConferencePublications V7.bib"
    conference_json_name = 'ConferencePublications V3.json'
    conference_csv_name = 'ConferencePublications V3.csv'
    conference_publication_obj = PublicationList2(conference_json_name, conference_csv_name, conference_bib_name)
    conference_publication_data = conference_publication_obj.read_bib_file()
    all_sorted_pub = conference_publication_obj.sort_by_date
    conference_publication_obj.writing_to_tex('AllConferencePublications.txt')
    conference_publication_obj.CreateCSV()
    print('\n \n The total conference publications found is   ====> ' + str(len(conference_publication_data.keys())))



    for selected_author in selected_author_list:
        selected_author_journal = exctract_publication_by_name(conference_publication_data, selected_author)
        conference_publication_obj.bib_data = selected_author_journal
        conference_publication_obj.sort_by_dat_no_Latex(selected_author_journal)
        conference_publication_obj.writing_to_tex('Student Publications\\' + selected_author + "_proceeding.txt")
        tex_file_name = 'Student Publications\\' + selected_author + "_proceeding_keys.txt"
        with open(tex_file_name, 'w', encoding='utf8') as txt_file:
            for item_key in selected_author_journal.keys():
                txt_file.write("%s\n" % item_key)
        txt_file.close()
        conference_publication_obj.all_sorted_items = []
        print('\n \n The total selected author conference publications found for ' + selected_author + ' is   ====> ' + str(len(selected_author_journal.keys())))
        selected_author_journal = []



if __name__ == "__main__":
    main()
