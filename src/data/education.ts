export interface EducationEntry {
  id: string;
  school: string;
  year: number;
  programme: string;
}

export const education: EducationEntry[] = [
  {
    id: "classic-mcpo",
    school: "МЦПО",
    year: 2025,
    programme: "Классический массаж",
  },
  {
    id: "medical-massage",
    school: "Медицинский институт реабилитации и косметологии им. З. М. Никифоровой",
    year: 2026,
    programme: "Оздоровительный медицинский массаж",
  },
  {
    id: "myofascial-drainage",
    school: "Школа адаптивного массажа А. Яковлева",
    year: 2026,
    programme: "Миофасциальный лимфодренаж",
  },
  {
    id: "strength-techniques",
    school: "Школа адаптивного массажа А. Яковлева",
    year: 2026,
    programme: "Силовые техники",
  },
  {
    id: "visual-palpatory-assessment",
    school: "Школа адаптивного массажа А. Яковлева",
    year: 2026,
    programme: "Визуальная и пальпаторная диагностика",
  },
  {
    id: "post-isometric-relaxation",
    school: "Школа адаптивного массажа А. Яковлева",
    year: 2026,
    programme: "Постизометрическая релаксация",
  },
  {
    id: "relax-adaptive-approach",
    school: "Школа адаптивного массажа А. Яковлева",
    year: 2026,
    programme: "Релакс массаж. Адаптивный подход",
  },
];
