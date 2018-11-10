
'''
This file and class is meant to do the following:
1. Read .bib file and extract its info in a dictionary variable. 
IMPORTANT: The bib file should follow certain formatting convention. Please refer to the attached .bib file. 
2. Export the data of bib file into CVS sheet. 
3. Export the data into .json file. 
4. Compare a provided list of publication in a text file with the list of publication in the object and provide the missing one in text file. i.e., the data in the original .bib file is the refernce.    
'''


import json
from datetime import datetime
import csv
import os
import difflib as diff
import re

'''
* when an object is created with this class "Publication list", the object will have all .bib data in the attribute "bib_data"
'''
class PublicationList:
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


# This methods exports the data of the bib file to the attribute dictionary  "bib_data" of hte object
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
    def sort_by_date(self):
        month_names_full = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']
        month_names_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_names = month_names_full + month_names_short
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

        with open('CSVTemp.csv', encoding='utf-8' ) as CSVFilePointer:
            CSVReaderPointer = csv.reader(CSVFilePointer)
            with open(self.csv_name, 'w+', newline='', encoding='utf-8' ) as CSVFilePointer2:
                CSVWriterPointer = csv.writer(CSVFilePointer2)
                CSVWriterPointer.writerow(CSVHeader)
                for Row in CSVReaderPointer:
                    CSVWriterPointer.writerow(Row)
        os.remove('CSVTemp.csv')


    '''
    This method open a text file "File_name_2_b_compared" and compare it with the list exist in object. 
    it has similarity index "similarity_percent" which determins whether the itme was found in hte original list or not. 
    '''



    def comparing_lists_V2(self, file_name_2_b_compared = 'Jornals_Web_Jul5.txt',similarity_percent = 0.85):
        print(' %%%%%%%%%%%%%%%%% Comparing the list in  ', file_name_2_b_compared, '   with the list in ', self.bib_name, '   %%%%%%%%%%%%%%%%%%%%%%%%%%%')
        import re
        import difflib as diff
        with open(file_name_2_b_compared, encoding='utf-8') as JournalToBeChecked:
            list_of_journal_in_website = list()
            for JournalLine in JournalToBeChecked:
                if '"' not in JournalLine:
                    continue
                selection_pattern = re.compile(r'"(.+)"')
                list_of_journal_in_website.append(selection_pattern.findall(JournalLine))

# This loop is to compare the list of the titles that was extracted from the website with the dictionary that was extracted from the bib file. Note that here we are trying to find the missing journal that are not in the website but they are in the bib file.
            list_of_keys_of_not_found_journal = []
        print('\n \n %%%%%%%%%%%%%%%%%%% The following titles are the not found in items:  \n ')
        for key in self.bib_data.keys():
            key_of_not_found_journal = 0
            max_matching_percent = 0

            for item in list_of_journal_in_website:
                matching_obj = diff.SequenceMatcher(None, self.bib_data[key]['title'].lower(), item[0].lower())
                matching_percent = matching_obj.ratio()
                if matching_percent> max_matching_percent:
                    max_matching_percent = matching_percent
                    key_of_not_found_journal = key
            if max_matching_percent < similarity_percent:
                list_of_keys_of_not_found_journal.append(key)
              #  print(max_matching_percent)
                print(self.bib_data[key_of_not_found_journal]['title'])
                #print(key_of_not_found_journal)

        print(' %%%%%%%%%%%%%%%%% Comparing the data in the bib file: ', self.bib_name,' to the list in the text file: ', file_name_2_b_compared)
        list_of_titles_of_not_found_journal = []
        for item in list_of_journal_in_website:
            title_of_not_found_journal = []

            max_matching_percent = 0
            for key in self.bib_data.keys():
                matching_obj = diff.SequenceMatcher(None, self.bib_data[key]['title'].lower(), item[0].lower())
                matching_percent = matching_obj.ratio()
                if matching_percent > max_matching_percent:
                    max_matching_percent = matching_percent
                    title_of_not_found_journal = item
            if max_matching_percent < similarity_percent:
                list_of_titles_of_not_found_journal.append(item)
                #  print(max_matching_percent)
                print(item)
                # print(key_of_not_found_journal)






        print( ' \n \n \n %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Now Checking for dublicated items in the list of the text file  ',file_name_2_b_compared,'  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print('\n \n %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% The following are dublicated titles in hte list of titles')
        for index1, item in enumerate(list_of_journal_in_website):
            for index2, item2 in enumerate(list_of_journal_in_website):
                if index1 == index2:
                    continue
                matching_obj2 = diff.SequenceMatcher(None, item[0], item2[0])
                matching_percent2 = matching_obj2.ratio()

                if matching_percent2 >.8:
                    print(item)
                    print(item2)
                    print('\n %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')


    # This method returns the dublicated items in a list in a list variable.
    def look_4_dublication_list(self, title_list, similarity_ratio = 0.95):
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Checking for dublicated items in the list %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% The following are dublicated titles in hte list of titles')
        import difflib as diff
        for item in list:
            for item2 in list:
                if item2 == item:
                    continue
                matching_obj = diff.SequenceMatcher(None, item, item2)
                matching_percent = matching_obj.ratio()
                if matching_percent > similarity_ratio:
                    print(item[0])
                    print(item2[0])


    # This method returns the dublicated items in the bib file of the bib object.
    def look_4_dublication(self, similarity_ratio  = .9):
        import difflib as diff
        no_dublication = True
        print('%%%%%%%%%%%%%%%%% Checking for Dublication in ', self.bib_name, '  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print('%%%%%%%%%%%%%%%%% The following paper\'s title are the dublicatied items in', self.bib_name, '  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        for key in self.bib_data.keys():
            for key_2 in self.bib_data.keys():
                if key_2 == key:
                    continue
                matching_obj = diff.SequenceMatcher(None,self.bib_data[key]['title'],self.bib_data[key_2]['title'])
                if matching_obj.ratio() > similarity_ratio:
                    no_dublication = False

                    print(self.bib_data[key]['title'])
                    print(self.bib_data[key_2]['title'])
                    print(key)
                    print(key_2)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        if no_dublication:
            print('No dublicated items in ', self.bib_name)
            print(print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% \n '))








    def comparing_lists(self, file_name_2_b_compared = 'Jornals_Web_Jul2.txt',  file_name_confused_itmes = 'ConfusedJournals.txt', file_name_not_found_items = 'NofFoundJournals.txt', similarity_percent = 80):

        with open(file_name_2_b_compared, encoding='utf-8') as JournalToBeChecked:
            with open(file_name_confused_itmes, 'w', encoding="UTF-8") as confused_journals_pointer:
                with open(file_name_not_found_items , 'w', encoding='utf-8') as NotFoundJournalPointer:
                    for JournalLine in JournalToBeChecked:
                        if '"' not in JournalLine:
                            continue
                        Found, Result = self.FindInexistentItems(JournalLine, similarity_percent)
                        if Found:
                            for item1 in Result:
                                for Line in item1:
                                    confused_journals_pointer.write(str(Line))
                                    print(Line)
                        else:
                            for item1 in Result:
                                for Line in item1:
                                    NotFoundJournalPointer.write(str(Line))
                                    print(Line)



    def FindInexistentItems(self, TextToBeChecked, SemilarityPercent):
        import difflib as diff
        import re
        #TitlePattern = re.compile(r'“([^"]*)”')
        TitlePattern = re.compile(r'"(.+)"')
        TitleToBeChecked = re.findall(TitlePattern, TextToBeChecked)
        Found = False
        MatchingList = []
        OriginalText = self.bib_data
        for ItemKey in OriginalText.keys():
            Item = OriginalText[ItemKey]
            OriginalTitle = Item['title']

            try:
                FullOriginalCitation = Item['author'] + ', ' + Item['title'] #+ ', ' + Item['journal'] +', p.p' + Item['pages'] + ', ' + Item['month']+ ', ' + Item['year']
            except:
                FullOriginalCitation = Item['author'] + ', ' + Item['title'] #+ ', ' + Item['booktitle'] +', p.p' + Item['pages'] + ', ' + Item['month']+ ', ' + Item['year']
            # else:
                # FullOriginalCitation = Item['author'] + ', ' + Item['title'] + ' JournalWas Not found in hte oreginal Bib File'

            SequanceResutl = diff.SequenceMatcher(None, OriginalTitle.lower(), TitleToBeChecked[0].lower())
            MatchingPercent = SequanceResutl.ratio()*100
            if MatchingPercent >= SemilarityPercent and MatchingPercent < 95 :
                Found = True
                # MatchingList.append([TitleToBeChecked[0].lower(), '====',MatchingPercent,'\n',OriginalTitle.lower(), '\n\n\n'])
                MatchingList.append(
                    [TextToBeChecked, '====', MatchingPercent, '\n', FullOriginalCitation, '\n\n\n'])

        if not Found:
            MatchingList.append([TitleToBeChecked[0].lower(), '====  0  ',  '\n\n\n'])

        return Found, MatchingList



def main():
    journal_bib_name = "DatabaseFiles\JournalPublications.bib"
    journal_json_name = 'JournalPublications.json'
    journal_csv_name = 'JournalPublications.csv'
    journal_publication_obj = PublicationList(journal_json_name, journal_csv_name, journal_bib_name)
    journal_publication_data = journal_publication_obj.read_bib_file()
    all_sorted_pub = journal_publication_obj.sort_by_date
    journal_publication_obj.writing_to_tex('AllJournalPublications.txt')
    journal_publication_obj.CreateCSV()
    print('\n \n The total journal publications found is   ====> ' + str(len(journal_publication_data.keys())))
    journal_publication_obj.look_4_dublication()
#    journal_publication_obj.comparing_lists_V2('Jornals_Web_Jul5.txt')

    conference_bib_name = "DatabaseFiles\ConferencePublications.bib"
    conference_json_name = 'ConferencePublications.json'
    conference_csv_name = 'ConferencePublications.csv'
    conference_publication_obj = PublicationList(conference_json_name, conference_csv_name, conference_bib_name)
    conference_publication_data = conference_publication_obj.read_bib_file()
    all_sorted_pub = conference_publication_obj.sort_by_date
    conference_publication_obj.writing_to_tex('AllConferencePublications.txt')
    conference_publication_obj.CreateCSV()
    print('\n \n The total conference publications found is   ====> ' + str(len(conference_publication_data.keys())))
    conference_publication_obj.look_4_dublication(similarity_ratio  = .95)
#    conference_publication_obj.comparing_lists_V2('Conference_web_Jul5.txt',similarity_percent = 0.95)

#UPDATED


if __name__ == "__main__":
    main()
