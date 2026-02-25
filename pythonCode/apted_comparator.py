from apted import APTED, Config
from dom_tree_converter import DOMTreeConverter


class APTEDComparator:
    """Compare DOM structures using APTED tree edit distance"""
    
    def __init__(self):
        self.converter = DOMTreeConverter()
        self.cache = {}  # Cache for performance
    
    def compare(self, html1, html2):
        """
        Compare two HTML DOMs using APTED
        
        Args:
            html1: First HTML string
            html2: Second HTML string
            
        Returns:
            dict with:
                - distance: Raw edit distance
                - normalized_distance: Normalized by tree size
                - similarity: 1.0 - normalized_distance
                - operations: Number of edits needed
        """
        # Check cache
        cache_key = (hash(html1), hash(html2))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Step 1: Convert HTML to trees
        tree1 = self.converter.html_to_tree(html1)
        tree2 = self.converter.html_to_tree(html2)
        
        # Step 2: Compute edit distance using APTED
        apted = APTED(tree1, tree2)
        distance = apted.compute_edit_distance()
        
        # Step 3: Normalize by tree size
        size1 = self._count_nodes(tree1)
        size2 = self._count_nodes(tree2)
        max_size = max(size1, size2)
        
        normalized_distance = distance / max_size if max_size > 0 else 0
        similarity = 1.0 - normalized_distance
        
        # Step 4: Build result
        result = {
            'distance': distance,
            'normalized_distance': normalized_distance,
            'similarity': similarity,
            'operations': distance,
            'tree1_size': size1,
            'tree2_size': size2
        }
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    def _count_nodes(self, tree):
        """Count total nodes in tree"""
        count = 1  # Current node
        for child in tree.children:
            count += self._count_nodes(child)
        return count
    
    def classify_by_distance(self, distance_info):
        """
        Classify based on normalized distance
        
        Args:
            distance_info: Result from compare()
            
        Returns:
            Classification string
        """
        normalized = distance_info['normalized_distance']
        
        if normalized == 0.0:
            return "identical"  # Perfect match
        elif normalized < 0.05:
            return "very_similar"  # Likely Nd2-data
        elif normalized < 0.15:
            return "similar"  # Likely Nd3-struct
        else:
            return "different"  # Likely Distinct

if __name__ == "__main__":
    comparator = APTEDComparator()
    