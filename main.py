import os
import re


def clean_path(path):
    # Заменяем "..\" и ".\" на пустую строку
    cleaned_path = re.sub(r'\.\.\\|\.\\', '', path)
    return os.path.normpath(cleaned_path)


def check_if_index_exists(source_directory, directory_path):
    full_path = clean_path(os.path.join(source_directory, os.path.normpath(directory_path)))
    index_path = os.path.join(full_path, "index.tsx")
    # Проверяем существование пути и является ли объект файлом
    path_exists = os.path.exists(index_path)
    is_file = os.path.isfile(index_path)
    return path_exists and is_file

def create_markdown_file(source_file_path, target_file_path, tag_added):
    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        source_code = source_file.read()

    imports = re.findall(import_pattern, source_code)

    if 'index' in source_file_path:
        parent_folder_name = os.path.basename(os.path.dirname(source_file_path))
        target_file_path = target_file_path.replace('index', parent_folder_name)

    with open(target_file_path, 'w', encoding='utf-8') as md_file:
        relative_source_path = os.path.relpath(source_file_path, os.path.dirname(target_file_path)).replace('\\', '/')
        md_file.write(f'Source: [{os.path.basename(source_file_path)}](./{relative_source_path.replace(" ", "%20")})\n\n')

        for import_name, imported_file in imports:
            import_name = import_name.strip()
            imported_file_path = os.path.join(os.path.dirname(source_file_path), imported_file)
            relative_imported_path = os.path.relpath(imported_file_path, os.path.dirname(target_file_path)).replace('\\', '/')
            is_Relative = False
            if len(import_name) > 0 and import_name[0].isupper():
                if import_name.strip() in imported_file:
                    if check_if_index_exists(source_directory, relative_imported_path):
                        is_Relative = True
                        relative_imported_path += '/' + import_name
            print(imports)
            if is_Relative:
                md_file.write(f'Imported: [{imported_file.split("/")[-1]}](./{relative_imported_path.replace(" ", "%20")})\n')
            else:
                md_file.write(f'Imported: [{imported_file.split("/")[-1]}]({imported_file})\n')

        md_file.write(f'```{file_extension}\n')
        md_file.write(source_code)
        md_file.write('\n```')
        if not tag_added:
            md_file.write('\nTags: #AppTS\n\n')

    print(f'File {target_file_path} successfully created from {file_extension} code!')

source_directory = r'D:\Projects\React Native\AppTS'
target_directory = r'D:\Projects\React Native\AppTS\docs'
exclude_folders = ['node_modules', 'test']
tag_added = False
import_pattern = r'import\s+(?:(?:\{([^\}]+)\})|[\w\d]+)\s+from\s+[\'"]((?:[^\'"/@]+/)+[^\'"]+)[\'"];'


for root, dirs, files in os.walk(source_directory):
    dirs[:] = [d for d in dirs if d not in exclude_folders]

    for file in files:
        if file.endswith('.ts') or file.endswith('.tsx'):
            source_file_path = os.path.join(root, file)
            file_extension = file.split('.')[-1]
            target_extension = 'md' if file_extension == 'ts' else 'md'
            relative_path = os.path.relpath(source_file_path, source_directory)
            target_file_path = os.path.join(target_directory, relative_path).replace(f'.{file_extension}', f'.{target_extension}')
            target_directory_path = os.path.dirname(target_file_path)
            os.makedirs(target_directory_path, exist_ok=True)
            create_markdown_file(source_file_path, target_file_path, tag_added)
            if not tag_added:
                tag_added = True
print('Conversion from .ts and .tsx to .md is complete.')
