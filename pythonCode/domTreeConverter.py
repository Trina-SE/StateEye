from apted.helpers import Tree
from lxml import html as lxml_html
import re


class DOMTreeConverter:
    """Convert HTML DOM to APTED tree structure"""
    
    def __init__(self, ignore_text=True, ignore_attributes=True):
        """
        Args:
            ignore_text: If True, ignore text content (recommended for structure comparison)
            ignore_attributes: If True, ignore element attributes (recommended)
        """
        self.ignore_text = ignore_text
        self.ignore_attributes = ignore_attributes
    
    def html_to_tree(self, html_string):
        """
        Convert HTML string to APTED Tree
        
        Args:
            html_string: Raw HTML as string
            
        Returns:
            APTED Tree object
        """
        # Step 1: Parse HTML with lxml
        try:
            doc = lxml_html.fromstring(html_string)
        except Exception as e:
            # If parsing fails, try wrapping in <div>
            html_string = f"<div>{html_string}</div>"
            doc = lxml_html.fromstring(html_string)
        
        # Step 2: Recursively build APTED tree
        tree = self._build_tree_recursive(doc)
        
        return tree
    
    def _build_tree_recursive(self, element):
        """
        Recursively convert lxml element to APTED Tree
        
        Args:
            element: lxml Element object
            
        Returns:
            APTED Tree node
        """
        # Step 1: Create node with tag name
        tag_name = element.tag
        
        # Step 2: Create APTED Tree node
        node = Tree(tag_name)
        
        # Step 3: Recursively add children
        for child in element:
            # Skip text nodes if configured
            if isinstance(child.tag, str):  # Only process element nodes
                child_node = self._build_tree_recursive(child)
                node.addkid(child_node)
        
        return node
    
    def strip_dom_content(self, html_string):
        """
        Remove text content and attributes from HTML
        Keeps only structure (tags and hierarchy)
        
        Args:
            html_string: Raw HTML
            
        Returns:
            Cleaned HTML with only structure
        """
        # Parse
        doc = lxml_html.fromstring(html_string)
        
        # Remove text and attributes
        for element in doc.iter():
            # Remove text content
            element.text = ""
            element.tail = ""
            
            # Remove all attributes
            element.attrib.clear()
        
        # Convert back to string
        from lxml import etree
        cleaned = etree.tostring(doc, encoding='unicode')
        
        return cleaned


# Example usage:
if __name__ == "__main__":
    converter = DOMTreeConverter()
    
    html = """
    <div class="product">
        <h1>Gaming Laptop</h1>
        <p>Price: $999</p>
        <button>Buy Now</button>
    </div>
    """
    
    tree = converter.html_to_tree(html)
    print("Tree created successfully!")
    print(f"Root node: {tree.name}")
    print(f"Children: {len(tree.children)}")