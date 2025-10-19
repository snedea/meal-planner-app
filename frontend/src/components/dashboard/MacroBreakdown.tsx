// Macro breakdown pie chart component

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { DailySummary } from '../../types/meal-log.types';

interface MacroBreakdownProps {
  summary: DailySummary;
}

const COLORS = {
  protein: '#3b82f6', // blue
  carbs: '#10b981', // green
  fats: '#f59e0b', // orange
};

export const MacroBreakdown: React.FC<MacroBreakdownProps> = ({ summary }) => {
  const data = [
    {
      name: 'Protein',
      value: summary.total_protein_g,
      target: summary.protein_target_g,
      color: COLORS.protein,
    },
    {
      name: 'Carbs',
      value: summary.total_carbs_g,
      target: summary.carbs_target_g,
      color: COLORS.carbs,
    },
    {
      name: 'Fats',
      value: summary.total_fats_g,
      target: summary.fats_target_g,
      color: COLORS.fats,
    },
  ];

  const hasData = data.some((item) => item.value > 0);

  if (!hasData) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No meals logged today
      </div>
    );
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${Math.round(value)}g`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `${Math.round(value)}g`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 space-y-2">
        {data.map((macro) => (
          <div key={macro.name} className="flex justify-between text-sm">
            <span className="text-gray-700">{macro.name}</span>
            <span className="font-medium">
              {Math.round(macro.value)}g / {Math.round(macro.target)}g
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
