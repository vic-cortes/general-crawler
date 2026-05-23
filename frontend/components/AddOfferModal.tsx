
import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { JobOffer, LanguageLevel } from '../types';
// Fix: Import ICONS from constants to resolve reference errors
import { ICONS } from '../constants';

const offerSchema = z.object({
  title: z.string().min(1, "Position title is required"),
  salaryMin: z.number().min(0, "Must be at least 0"),
  salaryMax: z.number().min(0, "Must be at least 0"),
  salaryCurrency: z.string().min(1, "Required"),
  workMode: z.enum(['Remote', 'Hybrid', 'On-site']),
  experienceLevel: z.enum(['Junior', 'Mid', 'Senior', 'Lead', 'Staff']),
  techStack: z.string().min(1, "Enter at least one tech stack (comma separated)"),
  benefits: z.string().min(1, "Enter at least one benefit (comma separated)"),
  sourceName: z.string().min(1, "Source name is required"),
  sourceUrl: z.string().url("Must be a valid URL"),
  languages: z.array(z.object({
    name: z.string().min(1, "Language name required"),
    level: z.enum(['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Native'])
  })).optional()
});

type OfferFormData = z.infer<typeof offerSchema>;

interface AddOfferModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (offer: Partial<JobOffer>) => void;
}

const AddOfferModal: React.FC<AddOfferModalProps> = ({ isOpen, onClose, onSave }) => {
  const { register, control, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<OfferFormData>({
    resolver: zodResolver(offerSchema),
    defaultValues: {
      salaryCurrency: 'USD',
      workMode: 'Remote',
      experienceLevel: 'Mid',
      languages: [{ name: 'English', level: 'B2' }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "languages"
  });

  const onSubmit = (data: OfferFormData) => {
    onSave({
      ...data,
      techStack: data.techStack.split(',').map(s => s.trim()),
      benefits: data.benefits.split(',').map(s => s.trim()),
      contractType: 'Full-time',
      createdAt: new Date().toISOString(),
      tags: []
    });
    reset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 transition-colors">
        <div className="px-8 py-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Analyze New Offer</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-8 space-y-6 max-h-[80vh] overflow-y-auto">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Position Title</label>
            <input 
              {...register('title')}
              placeholder="e.g. Senior Software Engineer"
              className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
            />
            {errors.title && <p className="text-xs text-red-500 font-medium">{errors.title.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Salary Min</label>
              <input 
                {...register('salaryMin', { valueAsNumber: true })}
                type="number" 
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              />
              {errors.salaryMin && <p className="text-xs text-red-500 font-medium">{errors.salaryMin.message}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Salary Max</label>
              <input 
                {...register('salaryMax', { valueAsNumber: true })}
                type="number" 
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              />
              {errors.salaryMax && <p className="text-xs text-red-500 font-medium">{errors.salaryMax.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Source Name</label>
              <input 
                {...register('sourceName')}
                placeholder="LinkedIn, Indeed..."
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              />
              {errors.sourceName && <p className="text-xs text-red-500 font-medium">{errors.sourceName.message}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Source URL</label>
              <input 
                {...register('sourceUrl')}
                placeholder="https://..."
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              />
              {errors.sourceUrl && <p className="text-xs text-red-500 font-medium">{errors.sourceUrl.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Work Mode</label>
              <select 
                {...register('workMode')}
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Experience</label>
              <select 
                {...register('experienceLevel')}
                className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value="Junior">Junior</option>
                <option value="Mid">Mid</option>
                <option value="Senior">Senior</option>
                <option value="Lead">Lead</option>
                <option value="Staff">Staff</option>
              </select>
            </div>
          </div>

          {/* Languages Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Language Requirements</label>
              <button 
                type="button" 
                onClick={() => append({ name: '', level: 'B2' })}
                className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline"
              >
                <ICONS.Plus /> Add Language
              </button>
            </div>
            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-2 items-end bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700 transition-colors">
                  <div className="flex-1 space-y-1">
                    <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Language</label>
                    <input 
                      {...register(`languages.${index}.name` as const)}
                      placeholder="e.g. English"
                      className="w-full px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                  <div className="w-32 space-y-1">
                    <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Level</label>
                    <select 
                      {...register(`languages.${index}.level` as const)}
                      className="w-full px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
                    >
                      <option value="A1">A1</option>
                      <option value="A2">A2</option>
                      <option value="B1">B1</option>
                      <option value="B2">B2</option>
                      <option value="C1">C1</option>
                      <option value="C2">C2</option>
                      <option value="Native">Native</option>
                    </select>
                  </div>
                  <button 
                    type="button" 
                    onClick={() => remove(index)}
                    className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  >
                    <ICONS.Trash />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Tech Stack (comma separated)</label>
            <input 
              {...register('techStack')}
              placeholder="React, TypeScript, Go..." 
              className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
            />
            {errors.techStack && <p className="text-xs text-red-500 font-medium">{errors.techStack.message}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">Benefits (comma separated)</label>
            <textarea 
              {...register('benefits')}
              rows={3}
              placeholder="Health insurance, Remote-first, Unlimited PTO..." 
              className="w-full px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500/20 focus:outline-none focus:border-blue-500 transition-colors"
            />
            {errors.benefits && <p className="text-xs text-red-500 font-medium">{errors.benefits.message}</p>}
          </div>

          <div className="flex gap-4 pt-4 sticky bottom-0 bg-white dark:bg-gray-800 transition-colors border-t border-gray-100 dark:border-gray-700 py-4">
            <button 
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-shadow shadow-sm disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save Data'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddOfferModal;
