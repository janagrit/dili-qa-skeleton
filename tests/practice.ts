// zero total hours is rejected”
// checkApprenticeshipRatio with totalHours = 0


/**
 *  {
    id: 'AP-004',
    area: 'apprenticeship',
    rule: 'Input integrity: apprentice hours cannot exceed total labor hours',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Apprentice hours above total hours are rejected instead of passing',
    tags: ['failure-mode', 'input-validation'],
  },
 */

  
//   checkApprenticeshipRatio(
//     apprenticeHours: number,
//     totalHours: number,
//     requiredRatio: number
//   )

//   checkApprenticeshipRatio(0, 0, 0.15);
// // Throws: "totalHours must be positive"