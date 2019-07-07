from functools import wraps
from datetime import datetime

# Function to log recieved messages to console and file
def log_it(id, message, func):
	st = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(st+"; ID: "+str(id)+"; Message: "+message+"; Entra a /"+func)
	f = open("TEL_BOT.txt", "a")
	f.write(st+"; ID: "+str(id)+"; Message: "+message+"; Entra a /"+func+'\n')
	f.close()

# Function to format the image analyzement results
def get_res_string(s_res):
    res = ''
	# Adds URLS of matching pages with image
    if s_res.pages_with_matching_images:
        res = res + '\n{} Pages with matching images retrieved:\n'.format(len(s_res.pages_with_matching_images))
        i = 1
        for page in s_res.pages_with_matching_images:
            res = res +'<a href="{}">Page {}</a>\n'.format(page.url, i)
            i += 1

    # Adds URLS of matching image
    if s_res.full_matching_images:
        res = res + '\n{} Full Matches found: \n'.format(len(s_res.full_matching_images))
        i = 1
        for image in s_res.full_matching_images:
            res = res +'<a href="{}">Full Match {}</a>\n'.format(image.url, i)
            i += 1

    # Adds URLS of partially matching image
    if s_res.partial_matching_images:
        res = res + '\n{} Partial Matches found: \n'.format(len(s_res.partial_matching_images))
        i = 1
        for image in s_res.partial_matching_images:
            res = res +'<a href="{}">Partial Match {}</a>\n'.format(image.url, i)
            i += 1

    # Adds found image antities and scores
    if s_res.web_entities:
        res = res + '\n{} Web entities found: \n'.format(len(s_res.web_entities))
        for entity in s_res.web_entities:
            res = res + '{} : %.2f'.format(entity.description) % (entity.score*100) + '%\n'

	# returns result
    return res