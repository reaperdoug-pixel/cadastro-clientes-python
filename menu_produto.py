"""
Módulo de compatibilidade/alias para menu_produtos.py
Permite importar sub_menu_produto ou sub_menu_produtos de menu_produto.
"""

from menu_produtos import sub_menu_estoque

# Alias no singular para máxima compatibilidade
sub_menu_produto = sub_menu_estoque
sub_menu_produtos = sub_menu_estoque
