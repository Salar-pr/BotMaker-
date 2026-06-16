from pytube import youtube 


def Download(link):
    youtubeObject = youtube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.Download()
    except:
        print("an error has occurred")
        print("download is completed successfully")


    link = input("enter the youtube video url: ")
    Download(link)