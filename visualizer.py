import argparse
import subprocess
import json
from graphviz import Digraph

def get_all_dependencies():
    # Получаем все зависимости проекта с помощью dotnet list package
    result = subprocess.run(['dotnet', 'list', 'package'], 
                            capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Error running dotnet list: {result.stderr}")

    try:
        dependencies = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to decode JSON. Output: " + result.stdout)

    return dependencies['dependencies']  # Возвращаем список зависимостей

def create_graph(dependencies):
    dot = Digraph(comment='Dependency Graph')

    # Добавляем узлы и ребра для всех зависимостей
    for dep in dependencies:
        dot.node(dep['name'], dep['name'])  # Добавляем узел для пакета
        for transitive in dep.get('transitive', []):
            dot.node(transitive['name'], transitive['name'])  # Добавляем узел для транзитивной зависимости
            dot.edge(dep['name'], transitive['name'])  # Добавляем ребро для транзитивной зависимости

    return dot

def main():
    parser = argparse.ArgumentParser(description='Visualize all .NET package dependencies in the project.')
    parser.add_argument('output_file', type=str, help='Output file for the dependency graph')
    
    args = parser.parse_args()

    try:
        dependencies = get_all_dependencies()  # Получаем все зависимости
        if not dependencies:
            print("No dependencies found for the project.")
            return

        graph = create_graph(dependencies)  # Создаем граф для всех зависимостей
        graph.render(args.output_file, format='png', cleanup=True)  # Сохраняем граф в файл
        print(f"Dependency graph saved to {args.output_file}.png")
        
        # Выводим количество зависимостей
        print(f"Total dependencies found: {len(dependencies)}")
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

