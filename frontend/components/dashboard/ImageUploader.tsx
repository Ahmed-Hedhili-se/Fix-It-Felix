"use client"
import React, { useCallback, useState } from 'react';
import { Upload, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import Image from 'next/image';

interface ImageUploaderProps {
    onImageSelected: (file: File) => void;
    selectedImage: File | null;
    onClear: () => void;
}

export function ImageUploader({ onImageSelected, selectedImage, onClear }: ImageUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onImageSelected(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            onImageSelected(e.target.files[0]);
        }
    };

    if (selectedImage) {
        return (
            <div className="relative w-full h-64 rounded-lg overflow-hidden border-2 border-primary/50 group">
                <Image
                    src={URL.createObjectURL(selectedImage)}
                    alt="Preview"
                    fill
                    className="object-cover"
                />
                <button
                    onClick={onClear}
                    className="absolute top-2 right-2 p-2 bg-black/60 text-white rounded-full hover:bg-red-600 transition-colors"
                >
                    <X size={20} />
                </button>
            </div>
        );
    }

    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
                "relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-all",
                isDragging
                    ? "border-primary bg-primary/10"
                    : "border-slate-700 bg-slate-900/50 hover:bg-slate-800 hover:border-slate-500"
            )}
        >
            <input
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleChange}
                accept="image/*"
            />
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className={cn("w-12 h-12 mb-4", isDragging ? "text-primary" : "text-slate-400")} />
                <p className="mb-2 text-sm text-slate-300">
                    <span className="font-semibold text-primary">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-slate-500">JPG, PNG, WEBP (Max 10MB)</p>
            </div>
        </div>
    );
}
