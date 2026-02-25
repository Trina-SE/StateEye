from apted_comparator import APTEDComparator
import numpy as np
from PIL import Image
import io


class FragmentClassifier:
    """
    Implements Algorithm 1 from FragGen paper
    Uses APTED for DOM comparison
    """
    
    def __init__(self, use_apted=True):
        """
        Args:
            use_apted: If True, use APTED. If False, use difflib (faster)
        """
        self.use_apted = use_apted
        
        if use_apted:
            self.dom_comparator = APTEDComparator()
        else:
            from difflib import SequenceMatcher
            self.sequence_matcher = SequenceMatcher
    
    def classify(self, fragment1, fragment2):
        """
        Algorithm 1 from FragGen paper
        
        Args:
            fragment1: First fragment (dict with 'dom' and 'screenshot')
            fragment2: Second fragment
            
        Returns:
            Classification: "Clone" | "Nd2-data" | "Nd3-struct" | "Distinct"
        """
# Compare DOM Structure (APTED HERE!)
        
        if self.use_apted:
            # Use APTED for accurate tree comparison
            dom_result = self.dom_comparator.compare(
                fragment1['dom'],
                fragment2['dom']
            )
            dom_identical = (dom_result['distance'] == 0)
        else:
            # Use difflib for fast comparison
            dom_identical = self._compare_dom_difflib(
                fragment1['dom'],
                fragment2['dom']
            )
        
# Compare Visual (if DOM matches)
        
        if dom_identical:
            # DOM structures are identical
            visual_identical = self._compare_visual(
                fragment1['screenshot'],
                fragment2['screenshot']
            )
            
            if visual_identical:
                return "Clone"  # Same structure, same appearance
            else:
                return "Nd2-data"  # Same structure, different data
        
# Map Child Fragments (if DOM differs)
        
        else:
            # DOM structures are different
            # Try to map child fragments
            can_map = self._map_child_fragments(fragment1, fragment2)
            
            if can_map:
                return "Nd3-struct"  # Structural duplication
            else:
                return "Distinct"  # Completely different
    
    def _compare_dom_difflib(self, dom1, dom2):
        """Fallback: Use difflib for DOM comparison"""
        from difflib import SequenceMatcher
        
        # Strip to structure only
        struct1 = self._strip_structure(dom1)
        struct2 = self._strip_structure(dom2)
        
        # Compare
        matcher = SequenceMatcher(None, struct1, struct2)
        similarity = matcher.ratio()
        
        return similarity > 0.95
    
    def _strip_structure(self, html):
        """Remove text and attributes, keep only tags"""
        import re
        no_text = re.sub(r'>[^<]+<', '><', html)
        no_attrs = re.sub(r'<(\w+)[^>]*>', r'<\1>', no_text)
        return no_attrs
    
    def _compare_visual(self, img1_bytes, img2_bytes):
        """Compare screenshots using histogram correlation"""
        img1 = Image.open(io.BytesIO(img1_bytes))
        img2 = Image.open(io.BytesIO(img2_bytes))
        
        # Resize to same size
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        
        # Convert to arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate histograms
        hist1 = np.histogram(arr1, bins=256)[0]
        hist2 = np.histogram(arr2, bins=256)[0]
        
        # Normalize
        hist1 = hist1 / hist1.sum()
        hist2 = hist2 / hist2.sum()
        
        # Correlation
        correlation = np.corrcoef(hist1, hist2)[0, 1]
        
        return correlation > 0.98
    
    def _map_child_fragments(self, frag1, frag2):
        """
        Try to map changed child fragments
        (Simplified version - full implementation would be recursive)
        """
        # For now, return False (assume Distinct)
        # Full implementation would recursively compare children
        return False

if __name__ == "__main__":
    classifier = FragmentClassifier(use_apted=True)
    