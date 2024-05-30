import { useEffect } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Separator } from "./ui/separator";

interface AlertPopupProps {
  items: string[];
  onClose: () => void;
}

const AlertPopup: React.FC<AlertPopupProps> = ({ items, onClose }) => {
  useEffect(() => {
    const outsideClickCall = (e: MouseEvent) => {
      const popupContent = document.querySelector(".popup-content");
      if (popupContent && !popupContent.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener("mousedown", outsideClickCall);

    return () => {
      document.removeEventListener("mousedown", outsideClickCall);
    };
  }, [onClose]);

  return (
  <AlertDialog open={true} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className=" text-slate-900">
            Alert
            <Separator></Separator>
            </AlertDialogTitle>
          <AlertDialogDescription>
            {items.map((item, index) => (
              <p key={index} className="text-md mb-6">
                {item}
              </p>
            ))}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction onClick={onClose}>Okay</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default AlertPopup;
