/**
 * DeleteConfirmationModal Component
 * 
 * A confirmation modal for destructive delete actions.
 * Features:
 * - Animated modal with backdrop
 * - Clear warning message
 * - Confirm/Cancel actions
 * - Keyboard support (Escape to cancel)
 */

'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeIn, scaleIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { AlertTriangle, X } from 'lucide-react';

interface DeleteConfirmationModalProps {
  /**
   * Whether the modal is open
   */
  isOpen: boolean;
  
  /**
   * Callback when modal is closed
   */
  onClose: () => void;
  
  /**
   * Callback when delete is confirmed
   */
  onConfirm: () => void;
  
  /**
   * Title of the modal
   */
  title: string;
  
  /**
   * Description/warning message
   */
  description: string;
  
  /**
   * Name of the item being deleted (for emphasis)
   */
  itemName?: string;
  
  /**
   * Loading state during deletion
   */
  isDeleting?: boolean;
  
  /**
   * Confirm button text
   * @default "Delete"
   */
  confirmText?: string;
  
  /**
   * Cancel button text
   * @default "Cancel"
   */
  cancelText?: string;
}

export function DeleteConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  itemName,
  isDeleting = false,
  confirmText = 'Delete',
  cancelText = 'Cancel',
}: DeleteConfirmationModalProps) {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isDeleting) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, isDeleting, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={!isDeleting ? onClose : undefined}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              variants={scaleIn}
              initial="hidden"
              animate="visible"
              exit="exit"
              className={cn(
                'relative w-full max-w-md rounded-xl',
                'bg-surface-container border border-outline-variant/15',
                'shadow-xl'
              )}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={onClose}
                disabled={isDeleting}
                className={cn(
                  'absolute top-4 right-4 p-1 rounded-lg',
                  'text-text-secondary hover:text-text-primary',
                  'hover:bg-surface-container-high',
                  'transition-colors',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Content */}
              <div className="p-6">
                {/* Icon */}
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-error/10 mb-4">
                  <AlertTriangle className="w-6 h-6 text-error" />
                </div>

                {/* Title */}
                <h2 className="text-title-lg text-text-primary font-semibold mb-2">
                  {title}
                </h2>

                {/* Description */}
                <p className="text-body-md text-text-secondary mb-4">
                  {description}
                </p>

                {/* Item name (if provided) */}
                {itemName && (
                  <div className="p-3 rounded-lg bg-surface-container-low border border-outline-variant/15 mb-6">
                    <p className="text-label-sm text-text-tertiary uppercase mb-1">
                      Item to delete
                    </p>
                    <p className="text-body-md text-text-primary font-medium break-all">
                      {itemName}
                    </p>
                  </div>
                )}

                {/* Warning */}
                <div className="p-3 rounded-lg bg-error/5 border border-error/20 mb-6">
                  <p className="text-body-sm text-error">
                    <strong>Warning:</strong> This action cannot be undone. All associated data will be permanently deleted.
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    onClick={onClose}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    {cancelText}
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={onConfirm}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    {isDeleting ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full"
                        />
                        Deleting...
                      </>
                    ) : (
                      confirmText
                    )}
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
