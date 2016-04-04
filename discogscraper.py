import subprocess, json, sys, os

class DiscogScraper():
    
    """
    Simple Class to retrieve data from the Discogs website
    It uses curl command to download the json files from the website
    """
    def __init__(self, token, search_string, song_title):
        self.main_url = 'https://api.discogs.com/'
        self.search_url = 'database/search'
        self.release_url = 'releases/'
        self.scrape_command = 'curl'
        self.json_path = 'json_releases/'
        self.token = token
        self.tempFile = ''
        self.search_string = search_string
        self.song_title = song_title.replace(" ", "%20")
        self.song_string = song_title
        if not os.path.isdir(self.json_path) and not os.path.exists(self.json_path):
            print "Create the Directory to store json files"
            os.makedirs(self.json_path)
    
    def search_command(self, search_string='', song_title='', page=1):
        """
            This function format the curl command to retrieve data from discogs
            It uses the token authentication - pass a valid Discogs Token
            It uses the initialized search_string and song_title
        """
        if (search_string!='' and song_title!=''):
            self.search_string = search_string.replace(" ", "%20")
            self.song_title = song_title.replace(" ", "%20")
        elif (search_string!=''):
            self.search_string = search_string.replace(" ", "%20")
        else:
            print("Use Initialization Values")
            
        self.tempFile = './' + self.json_path + self.search_string + self.song_title + '_' + str(page) + '.json'
        tempUrl = self.main_url + self.search_url + '?q=' + self.search_string + '&token=' + self.token
        if self.song_title:
            tempUrl += '&track=' + self.song_title
            
        command = self.scrape_command + ' \'' + tempUrl + '\' > ' + self.tempFile
        return command
        
    def release_command(self, rel_id):
        # curl "https://api.discogs.com/releases/1117108" --user-agent "FooBarApp/3.0" >> release_1117108.json
        relfile = './' + self.json_path + str(rel_id)+'.json'
        tempurl = self.main_url + self.release_url + str(rel_id)
        cmd = self.scrape_command + ' \'' + tempurl + '\'' + ' --user-agent \'discogsBrainFeederz/0.1\' >> ' + relfile
        
        return cmd
    
    def get_url(self, command):
        """
            This function download a single json file
        """
    
        data, error = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()
        #print data, error
        #try:
        #    with open(self.tempFile) as searchjson:
        #        json_data = json.load(searchjson)
        #        # check if not a json file
        #        return True
        #except IOError:
        #    print('File: - Not Created')
        #    return False
    
    def releasecollect(self):
        """
            This function downloads all the discogs pages for the research info used
            For each page download all the associated releases
        """
        releaseids = []
        nextsong = 0
        with open(self.tempFile) as jsonfile:
            jsondata = json.load(jsonfile)
            items = jsondata['pagination']['items']
            pp = jsondata['pagination']['per_page']
            results = jsondata['results']
            
        if items>0:
            pages = jsondata['pagination']['pages']
            if 'next' in jsondata['pagination']['urls']:
                nextsong = jsondata['pagination']['urls']['next']
            
            for i in results:
                if i['type'] == 'release':
                    #print i['id']
                    releaseids.append(i['id'])
        
        return releaseids, nextsong
    
    def get_tracklist(self, rel_id):
        tempfile = self.json_path + str(rel_id) + '.json'
        releasedictarray = []
        jdecoder = json.JSONDecoder()
        with open(tempfile) as jsonfile:
            text = jsonfile.read()
            while text:
                obj, idx = jdecoder.raw_decode(text)
                tracks = obj['tracklist']
                #print tracks
                releasedictarray.append(tracks)
                text = text[idx:].lstrip()
        return releasedictarray
        #print tempfile
    
    def chek_release(self, rel_id):
        tempfile = self.json_path + str(rel_id) + '.json'
        releasedictarray = []
        jdecoder = json.JSONDecoder()
        finded = False
        songdict = {}
        counter = 0
        songdict['styles'] = []
        with open(tempfile) as jsonfile:
            text = jsonfile.read()
            while text:
                obj, idx = jdecoder.raw_decode(text)
                tracks = obj['tracklist']
                
                for i in tracks:
                    if str(self.song_string).lower() in i['title'].lower():
                        finded = True
                        counter += 1
                        if counter == 1:
                            songdict['title'] = self.song_title
                            songdict['genres'] = obj['genres']
                            songdict['release_count'] = counter
                        else:
                            songdict['release_count'] = counter
                            songdict['genres'] = sorted(set(songdict['genres'] + obj['genres']))
                        if 'styles' in obj:
                            #print "Found: ", i['title'], obj['genres'], obj['styles']
                            songdict['styles'] = obj['styles']
                            songdict['styles'] = sorted(set(songdict['styles']))
                        
                text = text[idx:].lstrip()
        if finded==True:
            return songdict
    
    def merge_song_dict(self, dic1, dic2):
        if type(dic1) == type(dic2) == dict:
            if len(dic1.keys())>=len(dic2.keys()):
                target = dic1
                source = dic2
            else:
                if len(dic1.keys())==0:
                    target = dic1.update(dic2)
                    #return target
                else:
                    target = dic2
                    source = dic1
                
            for k in target.keys():        
                if type(target[k])==list:
                    target[k] = sorted(set(target[k]+source[k]))
                elif type(target[k])==int:
                    target[k] = target[k] + source[k]
                elif k=='title' and target['title']=="":
                    target['title'] = source['title']
            
            return target
        else:
            raise ValueError("Input two dictionaries")
        
    def create_songdict(self):
        songdict = {}
        songdict['title'] = ""
        songdict['genres'] = []
        songdict['styles'] = []
        songdict['release_count'] = 0
        return songdict