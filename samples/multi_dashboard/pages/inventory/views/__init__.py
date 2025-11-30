"""Inventory views."""
from .products import ProductsView
from .categories import CategoriesView
from .alerts import StockAlertsView
from .suppliers import SuppliersView

__all__ = ['ProductsView', 'CategoriesView', 'StockAlertsView', 'SuppliersView']
