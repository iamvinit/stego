from os import listdir
import argparse
import steghide

# returns a list of files with a particular extension
def list_files(directory, extension):
    return list(f for f in listdir(directory) if f.endswith('.' + extension))

def main(folderpath, sec_img_path, strKey, outputfolderpath):
    # add other image files as required
    files = list_files(folderpath,"png") + list_files(folderpath,"tiff") + list_files(folderpath,"bmp")
    
    for file in files:
        try:
            print("Performing Steganography on " + file)
            steghide.main(folderpath + "\\" + file, sec_img_path, strKey, outputfolderpath + "\\" + file[:file.rfind(".")] + "_stego" + file[file.rfind("."):])
            print("\n\n")
        except:
            print("This image cannot be used\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Performs Steganography on multiple image files')
    parser.add_argument("folderpath", help="Folder path")
    parser.add_argument("sec_img_path", help="Secret Image path")
    parser.add_argument("key", help="Key to encrypt Secret Image")
    parser.add_argument("-o", "--outputfolderpath", help="Output folder path")

    args = parser.parse_args()
    folderpath = args.folderpath
    sec_img_path = args.sec_img_path
    strKey = args.key
    if(args.outputfolderpath):
        outputfolderpath = args.outputfolderpath
    else:
        outputfolderpath = '.'
    main(folderpath, sec_img_path, strKey, outputfolderpath)