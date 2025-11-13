"""
Serveur Web Simple pour Visualisation CA Temps Réel.

Usage:
    python -m isinglab.server
    
Puis ouvrir: http://localhost:8000
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class CAViewerHandler(http.server.SimpleHTTPRequestHandler):
    """Handler pour servir les fichiers statiques + API CA."""
    
    def do_GET(self):
        """Gère les requêtes GET."""
        parsed = urlparse(self.path)
        
        # API: Liste HoF
        if parsed.path == '/api/hof':
            self.send_json_response(self.get_hof_rules())
            return
        
        # API: Meta-memory top N
        if parsed.path == '/api/memory':
            self.send_json_response(self.get_top_memory(limit=50))
            return
        
        # Servir fichiers statiques
        if parsed.path == '/' or parsed.path == '':
            self.path = '/viewer.html'
        
        # Servir depuis isinglab/static/
        static_dir = Path(__file__).parent / 'static'
        self.directory = str(static_dir)
        
        return super().do_GET()
    
    def get_hof_rules(self):
        """Charge les règles HoF."""
        hof_path = Path('isinglab/rules/hof_rules.json')
        if not hof_path.exists():
            return {'rules': []}
        
        with open(hof_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def get_top_memory(self, limit=50):
        """Charge top N règles de meta_memory."""
        memory_path = Path('results/meta_memory.json')
        if not memory_path.exists():
            return {'rules': []}
        
        with open(memory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        
        # Trier par composite
        def get_composite(r):
            scores = r.get('scores', {})
            return scores.get('composite', 0)
        
        sorted_rules = sorted(rules, key=get_composite, reverse=True)
        
        return {'rules': sorted_rules[:limit]}
    
    def send_json_response(self, data):
        """Envoie une réponse JSON."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(port: int = 8000):
    """Lance le serveur web."""
    # Changer vers la racine du projet
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    with socketserver.TCPServer(("", port), CAViewerHandler) as httpd:
        print("=" * 80)
        print(f"CA Viewer Server Running")
        print("=" * 80)
        print(f"\n  URL: http://localhost:{port}")
        print(f"  Press Ctrl+C to stop\n")
        print("=" * 80)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n[OK] Server stopped.")


def main():
    """Point d'entrée principal."""
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)


if __name__ == '__main__':
    main()

