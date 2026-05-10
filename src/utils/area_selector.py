"""
Area selector for detection 
Click 4 corners  to define playing area
"""

import cv2
import json
import os
import numpy as np

class CourtSelector:
    def __init__(self):
        self.points = []
        self.image = None
        self.window_name = 'Select Court Corners - Click 4 corners in order'
        
    def click_event(self, event, x, y, flags, param):
        """Mouse callback function"""
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append([x, y])
            
            # Draw point
            cv2.circle(self.image, (x, y), 8, (0, 255, 0), -1)
            cv2.putText(self.image, f"{len(self.points)}", (x+15, y-15),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            # Draw lines
            if len(self.points) > 1:
                cv2.line(self.image, tuple(self.points[-2]), tuple(self.points[-1]), 
                        (0, 255, 0), 2)
            
            # Close the polygon
            if len(self.points) == 4:
                cv2.line(self.image, tuple(self.points[-1]), tuple(self.points[0]), 
                        (0, 255, 0), 2)
                # Fill with transparent overlay
                overlay = self.image.copy()
                pts = np.array(self.points, np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(overlay, [pts], (0, 255, 0))
                cv2.addWeighted(overlay, 0.3, self.image, 0.7, 0, self.image)
                print("✅ Court boundary defined!")
                print("   Press ENTER to confirm or 'R' to reset")
            
            cv2.imshow(self.window_name, self.image)
    
    def select_court(self, video_path, output_path='data/outputs/court_config.json'):
        """
        Select court boundary by clicking 4 corners
        Returns: court_config dict
        """
        # Read first frame
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("❌ Could not read video!")
            return None
        
        # Resize if too large
        height, width = frame.shape[:2]
        if width > 1280:
            scale = 1280 / width
            frame = cv2.resize(frame, (1280, int(height * scale)))
        
        self.image = frame.copy()
        original_frame = frame.copy()
        
        print("\n🎾 Court Boundary Selector")
        print("=" * 60)
        print("📋 Instructions:")
        print("   1. Click 4 corners of the FRONT COURT in this order:")
        print("      ① Top-Left → ② Top-Right → ③ Bottom-Right → ④ Bottom-Left")
        print("   2. Press ENTER when done (after 4 points)")
        print("   3. Press 'R' to reset and start over")
        print("   4. Press 'Q' to quit")
        print("=" * 60)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.click_event)
        cv2.imshow(self.window_name, self.image)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 13:  # Enter key
                if len(self.points) == 4:
                    break
                else:
                    print(f"⚠️  Need 4 points, you have {len(self.points)}")
            
            elif key == ord('r') or key == ord('R'):  # Reset
                self.points = []
                self.image = original_frame.copy()
                cv2.imshow(self.window_name, self.image)
                print("🔄 Reset! Click 4 corners again.")
            
            elif key == ord('q') or key == ord('Q'):  # Quit
                print("❌ Cancelled")
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        
        # Save configuration
        court_config = {
            'corners': self.points,
            'video_width': width,
            'video_height': height
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(court_config, f, indent=2)
        
        print(f"\n💾 Court configuration saved to: {output_path}")
        print(f"   Corners: {self.points}")
        
        return court_config

if __name__ == "__main__":
    import sys
    video_path = sys.argv[1] if len(sys.argv) > 1 else 'data/raw/input_sample_video.mp4'
    
    selector = CourtSelector()
    config = selector.select_court(video_path)
    
    if config:
        print("\n✅ Court boundary setup complete!")
    else:
        print("\n❌ Setup cancelled")