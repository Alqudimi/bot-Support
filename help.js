// fetch('http://127.0.0.1:5000/api/users/create', {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json'
//   },
//   body: JSON.stringify({
//     name: "أحمد",
//     gender: "ذكر",
//     approximate_age: 25,
//   })
// })
// .then(response => response.json())
// .then(data => console.log(data));

// fetch('http://127.0.0.1:5000/api/messages/add', {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json'
//   },
//   body: JSON.stringify({
//     user_id: "5ec8a421-429c-4f35-9053-ad7ca17d4029",
//     timestamp: "2025-08-01T15:28:15Z",
//     sender_name: "فاطمة",
//     gender: "أنثى",
//     approximate_age: 25,
//     dominant_emotion: "محايد",
//     emotion_history_20s: [
//       {
//         timestamp: "2025-08-01T15:27:55Z",
//         emotion_percentage: {
//           neutral: 80,
//           surprised: 10,
//           angry: 10
//         }
//       },
//       {
//         timestamp: "2025-08-01T15:28:05Z",
//         emotion_percentage: {
//           neutral: 95,
//           surprised: 5,
//           angry: 0
//         }
//       },
//       {
//         timestamp: "2025-08-01T15:28:15Z",
//         emotion_percentage: {
//           neutral: 98,
//           surprised: 2,
//             angry: 0
//         }
//       }
//     ],
//     message_content: "شكراً جزيلاً على التحديث. سأراجع المستندات الآن."
//   })
// })
// .then(response => response.json())
// .then(data => console.log(data));

fetch('http://127.0.0.1:5000/api/history/aeab3c9b-948c-459e-8a3a-609ef8eaa01f/get', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
    body: JSON.stringify({
        user_id: "aeab3c9b-948c-459e-8a3a-609ef8eaa01f"
    })
})
.then(response => response.json())
.then(data => console.log(data));