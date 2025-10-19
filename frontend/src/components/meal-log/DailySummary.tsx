// Daily summary component for meal log page

import React from 'react';
import { DailySummary as DailySummaryType } from '../../types/meal-log.types';
import { Card } from '../common/Card';

interface DailySummaryProps {
  summary: DailySummaryType;
}

export const DailySummary: React.FC<DailySummaryProps> = ({ summary }) => {
  const macros = [
    {
      name: 'Protein',
      value: summary.total_protein_g,
      target: summary.protein_target_g,
      remaining: summary.protein_remaining_g,
      color: 'blue',
    },
    {
      name: 'Carbs',
      value: summary.total_carbs_g,
      target: summary.carbs_target_g,
      remaining: summary.carbs_remaining_g,
      color: 'green',
    },
    {
      name: 'Fats',
      value: summary.total_fats_g,
      target: summary.fats_target_g,
      remaining: summary.fats_remaining_g,
      color: 'orange',
    },
  ];

  return (
    <Card title="Today's Summary">
      <div className="space-y-4">
        {/* Calories */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium">Calories</span>
            <span className="text-sm">
              {Math.round(summary.total_calories)} / {summary.calorie_target}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${
                summary.calorie_remaining >= 0 ? 'bg-blue-600' : 'bg-red-600'
              }`}
              style={{
                width: `${Math.min((summary.total_calories / summary.calorie_target) * 100, 100)}%`,
              }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {summary.calorie_remaining >= 0
              ? `${Math.round(summary.calorie_remaining)} remaining`
              : `${Math.abs(Math.round(summary.calorie_remaining))} over`}
          </p>
        </div>

        {/* Macros */}
        {macros.map((macro) => (
          <div key={macro.name}>
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">{macro.name}</span>
              <span className="text-sm">
                {Math.round(macro.value)}g / {Math.round(macro.target)}g
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full bg-${macro.color}-600`}
                style={{
                  width: `${Math.min((macro.value / macro.target) * 100, 100)}%`,
                }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {macro.remaining >= 0
                ? `${Math.round(macro.remaining)}g remaining`
                : `${Math.abs(Math.round(macro.remaining))}g over`}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
};
