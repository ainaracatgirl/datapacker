import sys, os, json, glob, shutil
from zipfile import ZipFile

def loadcfg(txt, _eval=eval):
    lines = txt.splitlines()
    data = {}
    for line in lines:
        line = line.strip()
        if line == '': continue

        equality = line.split('=')
        key = equality[0].strip()
        value = _eval(equality[1].strip())
        data[key] = value
    return data

def readf(path, mode='r'):
    f = open(path, mode)
    ff = f.read()
    f.close()
    return ff

def writef(path, content, mode='w'):
    f = open(path, mode)
    f.write(content)

def processmcf(content, config):
    return content

def main(args):
    # Load config and create temporary folder
    config = loadcfg(readf("config.cfg"))
    if not ('tmp_folder' in config):
        config['tmp_folder'] = 'tmp/'
        print("warning: please specify a 'tmp_folder' field in the 'config.cfg' file")
    os.mkdir(config['tmp_folder'])

    # Create basic folder structure
    writef(config['tmp_folder'] + '/pack.mcmeta', json.dumps({
        "pack": {
            "pack_format": config['data_version'],
            "description": f"§c{config['name']} §2({config['version']}) §rby §9{config['author']}"
        }
    }))
    namespace = config['tmp_folder'] + '/data/' + config['id'] + '/'
    os.mkdir(config['tmp_folder'] + '/data')
    os.mkdir(config['tmp_folder'] + '/data/' + config['id'])
    os.mkdir(namespace + 'functions')
    os.mkdir(config['tmp_folder'] + '/data/minecraft/')
    os.mkdir(config['tmp_folder'] + '/data/minecraft/tags/')
    os.mkdir(config['tmp_folder'] + '/data/minecraft/tags/functions/')
    writef(config['tmp_folder'] + '/data/minecraft/tags/functions/load.json', json.dumps({
        "values": [
            config['id'] + ':' + '.'.join(config['init_func'].split('.')[:-1])
        ]
    }))
    writef(config['tmp_folder'] + '/data/minecraft/tags/functions/tick.json', json.dumps({
        "values": [
            config['id'] + ':' + '.'.join(config['main_func'].split('.')[:-1])
        ]
    }))

    print("info: base folder structure created")

    # Create function files
    for f in glob.glob('packfile/*.mcf'):
        infile = f
        outfile = namespace + 'functions/' + f[9:-3] + 'mcfunction'
        content = readf(infile)
        writef(outfile, processmcf(content, config))

    print("info: datapack created")

    # Save into a ZIP file
    if os.path.exists(config["id"] + '.zip'): os.remove(config["id"] + '.zip')
    with ZipFile(config["id"] + '.zip', 'w') as z:
        for f in glob.glob(config['tmp_folder'] + '/**', recursive=True):
            if f[len(config['tmp_folder']):] == '': continue
            z.write(f, f[len(config['tmp_folder']):])
    
    print("info: ZIP file created")
    
    shutil.rmtree(config['tmp_folder'])
    if 'copy_folder' in config:
        try: shutil.copyfile(config["id"] + '.zip', config['copy_folder'] + config["id"] + '.zip')
        except: print("warning: copy failed")

if __name__ == '__main__':
    main(sys.argv[1:])