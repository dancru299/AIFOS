# Tài liệu đầy đủ nội dung Portfolio — dancru.cloud

- **Nguồn dữ liệu:** `mpxhwlff_portfolio.sql`
- **Loại dữ liệu:** MySQL/MariaDB SQL dump từ database portfolio.
- **Phạm vi:** Trích xuất nội dung công khai/phục vụ website từ các bảng profile, settings, education, experience, skills, projects, certifications, translations.
- **Lưu ý bảo mật:** Các giá trị nhạy cảm như mật khẩu hash, access token, session payload không được copy nguyên văn vào tài liệu này.

## Mục lục
- [1. Tổng quan dữ liệu](#1-tng-quan-d-liu)
- [2. Nội dung Hero / Landing](#2-ni-dung-hero--landing)
- [3. Thông tin cá nhân & tài khoản quản trị](#3-thng-tin-c-nhn--ti-khon-qun-tr)
- [4. Học vấn](#4-hc-vn)
- [5. Kinh nghiệm / Hoạt động nghề nghiệp](#5-kinh-nghim--hot-ng-ngh-nghip)
- [6. Kỹ năng](#6-k-nng)
- [7. Dự án](#7-d-n)
- [8. Chứng chỉ & Thành tích](#8-chng-ch--thnh-tch)
- [9. Bản dịch / Translations](#9-bn-dch--translations)
- [10. Tin nhắn liên hệ](#10-tin-nhn-lin-h)
- [11. Tài liệu cấu trúc database](#11-ti-liu-cu-trc-database)
- [12. Phụ lục nội dung raw đã chuẩn hóa](#12-ph-lc-ni-dung-raw--chun-ha)

## 1. Tổng quan dữ liệu

- **Database:** `mpxhwlff_portfolio`
- **Thời điểm export:** May 31, 2026 at 05:27 PM
- **Server version:** 10.11.16-MariaDB-cll-lve
- **PHP version:** 8.4.21
- **Số bảng có schema:** 18
- **Số bảng có dữ liệu INSERT:** 11

| Table | Columns | Rows | Ghi chú |
| --- | --- | --- | --- |
| cache | 3 | 0 | Bảng hệ thống / phụ trợ |
| cache_locks | 3 | 0 | Bảng hệ thống / phụ trợ |
| certifications | 10 | 11 | Có dữ liệu website |
| contact_messages | 8 | 6 | Bảng hệ thống / phụ trợ |
| educations | 11 | 2 | Có dữ liệu website |
| experiences | 13 | 5 | Có dữ liệu website |
| failed_jobs | 7 | 0 | Bảng hệ thống / phụ trợ |
| job_batches | 10 | 0 | Bảng hệ thống / phụ trợ |
| jobs | 7 | 0 | Bảng hệ thống / phụ trợ |
| migrations | 3 | 14 | Bảng hệ thống / phụ trợ |
| password_reset_tokens | 3 | 0 | Bảng hệ thống / phụ trợ |
| personal_access_tokens | 10 | 2 | Bảng hệ thống / phụ trợ |
| portfolio_settings | 7 | 16 | Có dữ liệu website |
| projects | 25 | 4 | Có dữ liệu website |
| sessions | 6 | 0 | Bảng hệ thống / phụ trợ |
| skills | 10 | 14 | Có dữ liệu website |
| translations | 6 | 0 | Có dữ liệu website |
| users | 9 | 1 | Bảng hệ thống / phụ trợ |

## 2. Nội dung Hero / Landing

Phần này lấy từ bảng `portfolio_settings`. Các giá trị song ngữ được giữ đầy đủ theo tiếng Việt và tiếng Anh.

### Nhóm: `about`

#### `about_name`

- **ID:** 3
- **Type:** text
- **Created at:** 2026-02-10 10:59:05
- **Updated at:** 2026-02-10 10:59:05

Nguyễn Anh Đức

#### `about_description`

- **ID:** 4
- **Type:** text
- **Created at:** 2026-02-10 10:59:05
- **Updated at:** 2026-02-10 10:59:05

Tôi là sinh viên năm 3 ngành Công nghệ thông tin với niềm đam mê mãnh liệt về lập trình.

### Nhóm: `contact`

#### `contact_email`

- **ID:** 5
- **Type:** text
- **Created at:** 2026-02-10 10:59:05
- **Updated at:** 2026-02-10 10:59:05

nguyenanhduc@example.com

### Nhóm: `general`

#### `additional_skills`

- **ID:** 6
- **Type:** text
- **Created at:** 2026-02-14 09:13:18
- **Updated at:** 2026-05-30 01:26:28

**VI:** Giao tiếp, Làm việc nhóm, Quản lý thời gian, Tự học, Phát triển bản thân, Thích nghi

**EN:** Communication, Teamwork, Time Management, Self-Learning, Personal Development, Adaptability

#### `core_value_1_title`

- **ID:** 9
- **Type:** text
- **Created at:** 2026-04-29 23:38:09
- **Updated at:** 2026-04-29 23:38:09

**VI:** Mọi thứ trên đời đều chỉ là trải nghiệm

**EN:** Everything in life is just an experience.

#### `core_value_1_desc`

- **ID:** 10
- **Type:** text
- **Created at:** 2026-04-29 23:42:13
- **Updated at:** 2026-04-30 00:40:23

**VI:** Mọi thứ trên đời đều chỉ là trải nghiệm.

**EN:** Everything in life is just an experience.

#### `core_value_2_desc`

- **ID:** 11
- **Type:** text
- **Created at:** 2026-04-30 00:40:23
- **Updated at:** 2026-04-30 00:40:23

**VI:** Nếu bạn không gặp khó khăn, tức là bạn đang đứng yên.

**EN:** If you're not having any difficulties, it means you're standing still.

#### `resume_url`

- **ID:** 12
- **Type:** text
- **Created at:** 2026-04-30 01:26:06
- **Updated at:** 2026-05-29 11:46:05

/uploads/portfolio/files/sBiBoXAVGAKXaUlWqBeqwFe2VDpSsyBA66NOke1i.pdf

#### `core_value_3_desc`

- **ID:** 13
- **Type:** text
- **Created at:** 2026-05-30 01:20:52
- **Updated at:** 2026-05-30 01:20:52

**VI:** Càng nỗ lực, càng may mắn.

**EN:** The effort you try, the lucky you are.

#### `resume_ats_url`

- **ID:** 14
- **Type:** text
- **Created at:** 2026-05-30 01:38:41
- **Updated at:** 2026-05-30 01:38:41

/uploads/portfolio/files/VWWeP1g2enweOCCguUoaz2dDrVYszLksflYbBcq2.pdf

#### `social_github`

- **ID:** 15
- **Type:** text
- **Created at:** 2026-05-30 03:44:01
- **Updated at:** 2026-05-30 03:44:01

https://github.com/dancru299

#### `social_linkedin`

- **ID:** 16
- **Type:** text
- **Created at:** 2026-05-30 03:44:01
- **Updated at:** 2026-05-30 03:44:01

https://www.linkedin.com/in/dancru299/

#### `social_facebook`

- **ID:** 17
- **Type:** text
- **Created at:** 2026-05-30 03:44:01
- **Updated at:** 2026-05-30 03:44:01

https://www.facebook.com/

#### `social_youtube`

- **ID:** 18
- **Type:** text
- **Created at:** 2026-05-30 03:44:01
- **Updated at:** 2026-05-30 03:44:01

https://www.youtube.com/@ducdidauday299

### Nhóm: `hero`

#### `hero_title`

- **ID:** 1
- **Type:** text
- **Created at:** 2026-02-10 10:59:05
- **Updated at:** 2026-02-14 09:39:24

**VI:** Lập trình viên

**EN:** Web Developer

#### `hero_subtitle`

- **ID:** 2
- **Type:** text
- **Created at:** 2026-02-10 10:59:05
- **Updated at:** 2026-05-30 01:27:11

**VI:** Sinh viên năm 3 ngành CNTT, đam mê xây dựng web app, tool và xây dựng sản phẩm thực tế, ứng dụng cao.

**EN:** A third-year IT student passionate about building web apps, tools, and developing practical, high-application products.

## 3. Thông tin cá nhân & tài khoản quản trị

### User #1: Admin User

- **Name:** Admin User
- **Email:** nguyenanhduc2909@gmail.com
- **Role:** admin
- **Email verified at:** Chưa có dữ liệu
- **Created at:** 2026-02-10 10:17:45
- **Updated at:** 2026-05-29 11:09:43
- **Password / remember token:** Đã lược bỏ khỏi tài liệu vì là dữ liệu nhạy cảm.


## 4. Học vấn

### Cử nhân thực hành ngành Phát triển Web / Bachelor of Practice in Web Development

- **ID:** 1
- **Trường:** Cao đẳng FPT Polytechnic (FPL) / FPT Polytechnic College
- **Giai đoạn:** 2023 - 2025
- **GPA / Thành tích:** Valedictorian • GPA 3.81/4.0
- **Ảnh:** `/uploads/portfolio/bMlJbltYrKf2rn65irQblNgTGJgH0O7zBG11QRD3.jpg`
- **Sort order:** 1
- **Active:** 1
- **Created at:** 2026-02-10 11:04:59
- **Updated at:** 2026-05-30 01:05:41

#### Mô tả

**VI:** Xây dựng nền tảng về phát triển Web, tư duy sản phẩm và kỹ năng làm việc nhóm.

**EN:** Built a strong foundation in web development, product thinking, and teamwork.

### Kỹ sư Công nghệ Thông tin / Engineer in Information Technology

- **ID:** 3
- **Trường:** Học viện Công nghệ Bưu chính Viễn thông (PTIT) / Posts and Telecommunications Institute of Technology (PTIT)
- **Giai đoạn:** 2026 - 2030
- **GPA / Thành tích:** Không có dữ liệu
- **Ảnh:** `/uploads/portfolio/7bthH7QVkvH2IbeQJZpXuVfA2f9KjPhmGsmLPcKn.jpg`
- **Sort order:** 2
- **Active:** 1
- **Created at:** 2026-05-30 00:17:27
- **Updated at:** 2026-05-30 01:04:48

#### Mô tả

**VI:** Theo học chương trình Kỹ sư CNTT nhằm mở rộng nền tảng học thuật và chuyên môn dài hạn.

**EN:** Pursuing an IT engineering program to strengthen my academic and long-term technical foundation.

## 5. Kinh nghiệm / Hoạt động nghề nghiệp

### Software Developer (Independent Projects) — Dự án cá nhân & Cộng tác bên ngoài / Independent & Collaborative Projects

- **ID:** 4
- **Company:** Dự án cá nhân & Cộng tác bên ngoài / Independent & Collaborative Projects
- **Location:** Tại nhà / At home
- **Period:** 2024 - Đến nay
- **Rank:** Trung cấp
- **Sort order:** 2
- **Active:** 1
- **Created at:** 2026-02-14 11:10:45
- **Updated at:** 2026-05-29 14:14:05

#### Mô tả

**VI:** Chủ động tham gia các dự án phần mềm ngoài phạm vi học tập và công việc chính nhằm tích lũy kinh nghiệm thực tế. Tham gia vào nhiều giai đoạn phát triển sản phẩm từ phân tích yêu cầu, phát triển tính năng đến triển khai và vận hành.

**EN:** Actively contributed to software projects beyond academic and primary work responsibilities to gain real-world experience. Involved in various stages of product development, from requirements analysis and feature implementation to deployment and maintenance.

#### Thành tựu / trách nhiệm

**VI:** ['Tham gia phát triển nhiều dự án web và hệ thống quản lý thực tế', 'Làm việc với cả Frontend, Backend và cơ sở dữ liệu', 'Tiếp cận quy trình phát triển phần mềm trong môi trường cộng tác', 'Tự nghiên cứu và áp dụng công nghệ mới vào dự án', 'Xây dựng kinh nghiệm thực chiến ngoài chương trình đào tạo chính quy']

**EN:** ['Contributed to multiple real-world web applications and management systems', 'Worked across frontend, backend, and database development', 'Collaborated within real software development workflows', 'Researched and applied new technologies to project requirements', 'Built practical engineering experience beyond formal education']

#### Công nghệ / kỹ năng liên quan

- React
- Next.js
- Node.js
- TypeScript
- Laravel
- MongoDB
- MySQL
- Git
- Python
- REST API

### Thực tập sinh Fullstack / Fullstack Web Developer Intern — Cty Cổ phẩn ThinkLabs / ThinkLabs Joint Stock Company

- **ID:** 2
- **Company:** Cty Cổ phẩn ThinkLabs / ThinkLabs Joint Stock Company
- **Location:** Thanh Hóa / Thanh Hoa - VietNam
- **Period:** 05/2025 - 04/2026
- **Rank:** Intern
- **Sort order:** 3
- **Active:** 1
- **Created at:** 2026-02-10 11:04:59
- **Updated at:** 2026-05-29 14:41:32

#### Mô tả

**VI:** Tham gia phát triển các ứng dụng web và hệ thống quản lý doanh nghiệp trong môi trường thực tế. Làm việc với frontend, backend và cơ sở dữ liệu để triển khai các tính năng phục vụ người dùng.

**EN:** Contributed to the development of web applications and enterprise management systems. Worked across frontend, backend, and database layers to deliver business features and improve user experience.

#### Thành tựu / trách nhiệm

**VI:** ['Tham gia phát triển hệ thống ERP và quản lý nhân sự cho doanh nghiệp', 'Xây dựng giao diện quản trị bằng React và Ant Design', 'Phát triển API bằng Node.js và làm việc với MongoDB', 'Tham gia phân tích yêu cầu và xử lý lỗi trong quá trình phát triển sản phẩm']

**EN:** ['Participate in developing ERP and human resource management systems for businesses.', 'Build admin interfaces using React and Ant Design.', 'Develop APIs using Node.js and work with MongoDB.', 'Participate in requirements analysis and bug fixing during product development.']

#### Công nghệ / kỹ năng liên quan

- React
- Node.js
- Java
- MongoDB
- REST API
- Microservice

### Giảng viên Lập trình & Robotics / Programming & Robotics Instructor — Trung tâm sáng tạo công nghệ 8BIT / 8-BIT Technology Innovation Center

- **ID:** 3
- **Company:** Trung tâm sáng tạo công nghệ 8BIT / 8-BIT Technology Innovation Center
- **Location:** Thanh Hóa / Thanh Hoa - VietNam
- **Period:** 09/2025 - 04/2026
- **Rank:** Giảng viên
- **Sort order:** 4
- **Active:** 1
- **Created at:** 2026-02-10 11:04:59
- **Updated at:** 2026-05-29 14:46:29

#### Mô tả

**VI:** Giảng dạy lập trình và robotics cho học sinh tiểu học và THCS thông qua các môn học như Scratch, Python và Robotics. Đồng thời tham gia xây dựng giáo trình, thiết kế bài giảng và hỗ trợ các hoạt động giáo dục công nghệ tại trung tâm.

**EN:** Taught programming and robotics to elementary and middle school students through courses such as Scratch, Python, and Robotics. Also contributed to curriculum development, lesson planning, and educational technology activities.

#### Thành tựu / trách nhiệm

**VI:** ['Đạt danh hiệu Nhân viên Part-time Xuất sắc nhất', 'Đạt thành tích doanh thu cao nhất trong nhóm nhân sự Part-time', 'Tham gia phát triển hệ thống LMS phục vụ hoạt động đào tạo của trung tâm', 'Thiết kế và giảng dạy các khóa học Scratch, Python và Robotics cho học sinh', 'Hỗ trợ xây dựng tài liệu và lộ trình học tập phù hợp với từng độ tuổi']

**EN:** ['Recognized as Outstanding Part-time Employee', 'Achieved the highest revenue performance among part-time staff', "Contributed to the development of the center's Learning Management System (LMS)", 'Designed and delivered Scratch, Python, and Robotics courses for students', 'Supported curriculum and learning roadmap development for different age groups']

#### Công nghệ / kỹ năng liên quan

- Python
- Scratch
- Robotics
- STEM Education
- Curriculum Design
- Classroom Management
- Public Speaking

### Sinh viên ngành Công nghệ Thông tin / Software Engineering Student — Học viện Công nghệ Bưu chính Viễn thông (PTIT) / Posts and Telecommunications Institute of Technology (PTIT)

- **ID:** 5
- **Company:** Học viện Công nghệ Bưu chính Viễn thông (PTIT) / Posts and Telecommunications Institute of Technology (PTIT)
- **Location:** Học từ xa / Remote Learning
- **Period:** 01/2026-2030
- **Rank:** Bachelor's Degree
- **Sort order:** 5
- **Active:** 1
- **Created at:** 2026-02-14 11:15:53
- **Updated at:** 2026-05-29 14:52:13

#### Mô tả

**VI:** Theo học chương trình đại học ngành Công nghệ Thông tin theo hình thức từ xa nhằm nâng cao nền tảng học thuật, kiến thức chuyên sâu về khoa học máy tính và kỹ thuật phần mềm, đồng thời duy trì công việc thực tế trong ngành.

**EN:** Pursuing a Bachelor's degree in Information Technology through a remote learning program while continuing professional work experience in software development.

#### Thành tựu / trách nhiệm

**VI:** ['Tiếp tục theo đuổi chương trình đại học ngành Công nghệ Thông tin', 'Kết hợp học tập học thuật với kinh nghiệm thực tế trong ngành phần mềm', 'Mở rộng kiến thức về khoa học máy tính, hệ thống và kỹ thuật phần mềm', 'Xây dựng nền tảng dài hạn cho định hướng Software Engineer']

**EN:** ["Pursuing a Bachelor's degree in Information Technology", 'Combining academic studies with hands-on industry experience', 'Expanding knowledge in computer science, systems, and software engineering', 'Building a strong foundation for a long-term software engineering career']

#### Công nghệ / kỹ năng liên quan

- Computer Science
- Software Engineering
- Information Systems
- Algorithms
- Databases

### Học viên - Chương trình Đào tạo Nhân tài AI Thực chiến / Trainee - Vingroup Practical AI Talent Development Program — Tập đoàn Vingroup (phối hợp VinUniversity) / Vingroup Corporation (in collaboration with VinUniversity)

- **ID:** 6
- **Company:** Tập đoàn Vingroup (phối hợp VinUniversity) / Vingroup Corporation (in collaboration with VinUniversity)
- **Location:** Hà Nội (VinUni - Vinhomes Ocean Park, Gia Lâm) / Hanoi, Vietnam (VinUniversity Campus, Vinhomes Ocean Park)
- **Period:** Tháng 4/2026 - Tháng 7/2026 (12 tuần)
- **Rank:** Trainee
- **Sort order:** 6
- **Active:** 1
- **Created at:** 2026-05-03 16:14:40
- **Updated at:** 2026-05-30 01:17:09

#### Mô tả

**VI:** Tham gia chương trình đào tạo AI thực chiến 12 tuần toàn thời gian của Tập đoàn Vingroup (phối hợp VinUni). Chương trình theo mô hình 3+3+6: 3 tuần nền tảng, 3 tuần mô phỏng thực chiến và 6 tuần làm dự án thực tế tại doanh nghiệp thuộc hệ sinh thái Vingroup. Tập trung phát triển kỹ năng AI ứng dụng, tư duy sản phẩm và làm việc trực tiếp với mentor là chuyên gia dự án AI.

**EN:** Participated in Vingroup's 12-week full-time Practical AI Talent Development Program (Foundation Level), implemented in collaboration with VinUniversity. Structured in 3+3+6 model: 3 weeks foundational training, 3 weeks simulated real-world scenarios, and 6 weeks hands-on project work at Vingroup ecosystem companies. Focused on applied AI skills, product thinking, and real business impact under mentorship of industry AI project managers.

#### Thành tựu / trách nhiệm

**VI:** ['Hoàn thành chương trình đào tạo AI thực chiến toàn thời gian kéo dài 12 tuần theo mô hình 3+3+6 của Vingroup và VinUniversity', 'Xây dựng các giải pháp AI ứng dụng sử dụng LLM, RAG, AI Agents và MLOps cho các bài toán doanh nghiệp mô phỏng và thực tế', 'Thực hiện dự án AI theo nhóm dưới sự hướng dẫn trực tiếp của chuyên gia ngành, áp dụng quy trình phát triển sản phẩm AI từ ý tưởng đến triển khai', 'Đạt chuẩn năng lực theo khung SFIA thông qua các bài đánh giá kỹ năng kỹ thuật, tư duy sản phẩm và năng lực làm việc dự án']

**EN:** ["Completed Vingroup's competitive 12-week full-time Practical AI Talent Development Program", 'Developed AI applications using Python, LLMs, RAG pipelines, AI Agents, and MLOps workflows', 'Worked on real-world business use cases within the Vingroup ecosystem under direct mentorship from AI industry practitioners', 'Demonstrated competencies aligned with the SFIA framework in software engineering, AI development, and product thinking']

#### Công nghệ / kỹ năng liên quan

- Python
- OpenAI API
- LangGraph
- AI Agents
- Software Testing
- Playwright
- Pytest
- Docker
- GitHub Actions
- MLOps

## 6. Kỹ năng

### Backend

| Tên | Proficiency | Icon | Icon URL | Sort | Active |
| --- | --- | --- | --- | --- | --- |
| Node.js | 85 | Server | /storage/portfolio/icons/nNh4JPstNh2P4NLMZOYW7hE8ZxC8uPUeT97aN28h.png | 5 | 1 |
| Php | 70 | Server | /storage/portfolio/icons/gRWu5PQSXH8NX7v56Fa41wUZzd0j4ewaUpvMCcmn.png | 6 | 1 |
| Laravel/PHP | 75 | Server | /storage/portfolio/icons/9fOZlvg8ejitlUkhVhDOyiKLltilNJlsz0RerJMl.png | 7 | 1 |
| Javascript | 85 | Server | /storage/portfolio/icons/D1E9VdCw2AVNvacxmgYzgztSxdL7jX5vzonY8Oyr.jpg | 8 | 1 |
| Python | 0 | None | /uploads/portfolio/icons/9DMPl8klfnzlyQO5WjyQUMeBU8Yl8X1kRClVqFS7.png | 13 | 1 |

### Cơ sở dữ liệu / Database

| Tên | Proficiency | Icon | Icon URL | Sort | Active |
| --- | --- | --- | --- | --- | --- |
| MongoDB | 85 | Database | /storage/portfolio/icons/QiyabGT7ovh6C4L35Wi1ewAWgdbKtLRy8VCSFCGs.jpg | 10 | 1 |
| MySQL | 85 | Database | /storage/portfolio/icons/rNQo1DjilVAKgxQC4dGk6XoqdC1FMQVKFkaifl7L.png | 12 | 1 |
| PostgreSQL | 0 | None | /uploads/portfolio/icons/7YAooghZqnma6lVGTuhR0N7JymhfO4GhXEFwsfVJ.png | 14 | 1 |

### Frontend

| Tên | Proficiency | Icon | Icon URL | Sort | Active |
| --- | --- | --- | --- | --- | --- |
| React/Next.js | 90 | Cpu | /storage/portfolio/icons/9jk0MonUA1pSf7llharXYZwXnhYGSqdOnbkjFM06.png | 1 | 1 |
| Vue.js | 85 | Cpu | /storage/portfolio/icons/GnftYD7PctDEQu5QIEK0ge64DRAwh7QeuQXaun6x.png | 2 | 1 |
| TypeScript | 88 | Cpu | /storage/portfolio/icons/hdt6iPnvdluWWViYftjwZ1vyOk8eODiKCC9bp1UH.png | 3 | 1 |
| Tailwind CSS | 95 | Cpu | /storage/portfolio/icons/KXURTGx5KHgmmdiSD3z1ELvagvlRchmgt0jUINg9.png | 4 | 1 |
| HTML/CSS | 0 | None | /storage/portfolio/icons/X1iEv5EXR5jV2P72I8FYFNwm66vPfE9rNyCh6Swj.png | 11 | 1 |
| JavaScript | 0 | None | /storage/portfolio/icons/uEVQUUMWZ2ql7MNhevoZKI03pVyGp5mrNsDotGPf.jpg | 12 | 1 |

## 7. Dự án

### LavishStay - Nền tảng quản lý và đặt phòng khách sạn / LavishStay - Hospitality Booking & Management Platform

- **ID:** 1
- **Slug:** h
- **Category:** Dự án tốt nghiệp / Graduation Project
- **Role:** Trưởng nhóm & Backend Developer / Leader & Backend Developer
- **Duration:** ~ 3 months
- **Team:** 6 people
- **Status:** Completed
- **Start date:** 2025-03-10
- **End date:** 2025-05-10
- **Live URL:** https://lavishstay.dancru.cloud/
- **GitHub URL:** https://github.com/markprovjp/LAVISHSTAY
- **Image:** `/storage/portfolio/jff4CEYZgL42LOE3BJxPYuzYEbkOjIRxp1TJB9eW.png`
- **Sort order:** 1
- **Active:** 1
- **Created at:** 2026-02-10 11:14:02
- **Updated at:** 2026-05-30 04:01:28

#### Mô tả ngắn

**VI:** Hệ thống quản lý & đặt phòng khách sạn trực tuyến

**EN:** Online hotel management and booking system

#### Mô tả dài

**VI:** Trong nhiều mô hình khách sạn và homestay lớn, quy trình quản lý phòng, đặt phòng và theo dõi khách hàng thường được thực hiện thủ công hoặc phân tán trên nhiều công cụ khác nhau.

LavishStay được xây dựng nhằm số hóa quy trình vận hành lưu trú, giúp quản lý thông tin phòng, khách hàng, trạng thái đặt phòng và dữ liệu giao dịch trên một hệ thống tập trung.

**EN:** Many big hotels and homestays still rely on manual processes or disconnected tools for room management and reservation tracking.

LavishStay was developed to digitize hospitality operations by centralizing room management, customer information, booking status, and transaction workflows into a single platform.

#### Nội dung chi tiết

**VI:** LavishStay là dự án tốt nghiệp được xây dựng nhằm mô phỏng và triển khai thực tế các quy trình vận hành của hệ thống khách sạn và lưu trú hiện đại.

Hệ thống cho phép khách hàng tìm kiếm và đặt phòng trực tuyến, trong khi phía quản trị có thể quản lý phòng, trạng thái đặt phòng, thông tin khách hàng và dữ liệu vận hành trên một dashboard tập trung.

Phần trọng tâm của dự án nằm ở việc xây dựng backend với kiến trúc API phục vụ nhiều nhóm chức năng khác nhau, đảm bảo khả năng mở rộng, quản lý dữ liệu tập trung và hỗ trợ tích hợp frontend một cách linh hoạt.

**EN:** LavishStay is a graduation project designed to simulate and implement real-world hospitality management workflows.

The platform allows customers to browse and book rooms online, while administrators can manage rooms, reservation statuses, customer information, and operational data through a centralized dashboard.

The main focus of the project was backend development, including API architecture, database design, business workflow implementation, and scalable system integration.

#### Trách nhiệm

**VI:** Thiết kế và phát triển phần lớn hệ thống backend.
Xây dựng REST API phục vụ frontend và dashboard quản trị.
Thiết kế cơ sở dữ liệu và các luồng nghiệp vụ đặt phòng.
Xử lý xác thực, phân quyền và bảo mật dữ liệu.
Xây dựng hệ thống quản lý phòng, đặt phòng và khách hàng.
Tối ưu luồng xử lý dữ liệu giữa frontend và backend.
Tham gia triển khai, kiểm thử và tích hợp hệ thống.

**EN:** Developed the majority of the backend system.
Built REST APIs for frontend and administrative dashboards.
Designed database schemas and booking workflows.
Implemented authentication, authorization, and security layers.
Developed room, reservation, and customer management modules.
Optimized data communication between frontend and backend.
Participated in deployment, testing, and system integration.

#### Tech stack

- Laravel
- PHP
- MySQL
- REST API
- JWT Authentication
- Tailwind CSS
- React
- JavaScript
- Cloud Storage

#### Features

- **VI:** Đặt phòng trực tuyến

**EN:** Online booking system
- **VI:** Quản lý trạng thái đặt phòng

**EN:** Reservation status tracking
- **VI:** Quản lý dữ liệu vận hành tập trung

**EN:** Centralized operational management

#### Metrics / Highlights

-   - **label:** **VI:** Backend-Centric Architecture

**EN:** Backend-Centric Architecture
  - **value:** **VI:** Phần lớn hệ thống nghiệp vụ được triển khai ở backend.

**EN:** Most business logic was implemented on the backend layer.
-   - **label:** **VI:** REST API Platform

**EN:** REST API Platform
  - **value:** **VI:** Hệ thống API phục vụ frontend và dashboard quản trị.

**EN:** REST API architecture supporting both customer-facing and admin interfaces.
-   - **label:** **VI:** Booking Workflow Management

**EN:** Booking Workflow Management
  - **value:** **VI:** Quản lý luồng đặt phòng và trạng thái vận hành tập trung.

**EN:** Centralized booking workflow and reservation status management.

#### Gallery images

- /uploads/portfolio/gallery/ot8boC0GuW25uE63uvG4iNyDZeOEvf687Ih7sZd3.jpg
- /uploads/portfolio/gallery/Qj2jbjrZQyu34epkYGh4tROhxLFs6g8VdhnwDIGV.jpg
- /uploads/portfolio/gallery/UrW84bKaxHdf9PnvdmadgRf1i7jCTDtA7OmbKKCm.jpg
- /uploads/portfolio/gallery/FiBmN2aArAA8dOE0ABTn4IfEAGVH4H0wPklXgkFv.jpg
- /uploads/portfolio/gallery/OopMDnkcrWxyaD6X6ycCLBZ5P4d7GVWmG2jQdO90.jpg

### FaceConst - Nhà đẹp giá tốt / FaceConst - Beautiful homes at great prices

- **ID:** 4
- **Slug:** faceconst---nhà-đẹp-giá-tốt / faceconst---beautiful-homes-at-great-prices
- **Category:** Mạng xã hội / A social network
- **Role:** Nhà phát triển / Developer
- **Duration:** Không có dữ liệu
- **Team:** Không có dữ liệu
- **Status:** Live
- **Start date:** 2025-12-24
- **End date:** 2026-03-21
- **Live URL:** https://nhadepgiatot.shinigami.io.vn/
- **GitHub URL:** No public
- **Image:** `/storage/portfolio/B9rzs7JG1wZSG5m3XSynW71ndTWH5V0Crc7JzMtN.png`
- **Sort order:** 3
- **Active:** 1
- **Created at:** 2026-02-14 12:31:38
- **Updated at:** 2026-05-30 03:32:19

#### Mô tả ngắn

**VI:** Mạng xã hội dành riêng cho ngành xây dựng.

**EN:** A social network dedicated to the construction industry.

#### Mô tả dài

**VI:** Mạng xã hội dành riêng cho ngành xây dựng. Giao quen thuộc diện giống Facebook

**EN:** A social network dedicated to the construction industry. Familiar interactions are similar to Facebook.

#### Nội dung chi tiết

_Không có dữ liệu_

#### Trách nhiệm

**VI:** Tôi cùng với 4 người khác đảm nhiệm vai trò phát triển mạng xã hội này

**EN:** I, along with four others, were responsible for developing this social network.

#### Tech stack

- React
- Laravel
- TaiwindCss
- Livewire
- Alpine.js

#### Features

_Không có dữ liệu_

#### Metrics / Highlights

_Không có dữ liệu_

#### Gallery images

_Không có dữ liệu_

### Tổ chức sự kiện Thanh Hóa / Thanh Hoa Event Organization

- **ID:** 2
- **Slug:** tổ-chức-sự-kiện-thanh-hóa / thanh-hoa-event-organization
- **Category:** Landing page + Admin
- **Role:** Nhà phát triển / Developer
- **Duration:** Không có dữ liệu
- **Team:** Không có dữ liệu
- **Status:** Live
- **Start date:** 2024-10-07
- **End date:** 2025-01-15
- **Live URL:** https://tochucsukienthanhhoa.vn/
- **GitHub URL:** No git
- **Image:** `/storage/portfolio/9kmvmCYYYQyKyjDb3rTAjkOj7HuX3jGtB9TWkDkl.png`
- **Sort order:** 5
- **Active:** 1
- **Created at:** 2026-02-14 12:05:32
- **Updated at:** 2026-05-30 03:32:11

#### Mô tả ngắn

**VI:** Website landing page

**EN:** Website landing page

#### Mô tả dài

**VI:** Website landing page quảng cáo cho cty liên quan đến tổ chức sự kiện: Đám cưới, đám hỏi, tiệc, sự kiện, đám tang, rạp ngoài trời,..

**EN:** This website landing page advertises a company involved in event organization: weddings, engagements, parties, events, funerals, outdoor venues, etc.

#### Nội dung chi tiết

_Không có dữ liệu_

#### Trách nhiệm

**VI:** Lên kế hoạch từ A -> Z, từ lên design cho tới thu thập thông tin và code web (no AI)

**EN:** Planning from A to Z, from design to information gathering and web coding (no AI).

#### Tech stack

- Laravel
- HTML
- CSS
- JS

#### Features

_Không có dữ liệu_

#### Metrics / Highlights

_Không có dữ liệu_

#### Gallery images

- /uploads/portfolio/gallery/R1PRFOJAxnX5PA3bD6SWmE0TLoOll3rRFq27dwdy.png

### Portfolio - Nền tảng Portfolio Full-stack cá nhân / Portfolio - Full-stack Personal Portfolio Platform

- **ID:** 3
- **Slug:** portfolio
- **Category:** Dự án cá nhân / Personal Project
- **Role:** Full-stack Developer / Product Designer
- **Duration:** Không có dữ liệu
- **Team:** 1 people
- **Status:** Live
- **Start date:** 2026-01-03
- **End date:** 2026-05-30
- **Live URL:** https://dancru.cloud/
- **GitHub URL:** Không có dữ liệu
- **Image:** `/storage/portfolio/1mXcLIenW4sxLHFVi39U3bgJgJC93OkC6fSENMaE.png`
- **Sort order:** 6
- **Active:** 1
- **Created at:** 2026-02-14 12:20:35
- **Updated at:** 2026-05-30 04:15:40

#### Mô tả ngắn

**VI:** Website portfolio full-stack được xây dựng nhằm trình bày dự án, kinh nghiệm và kỹ năng cá nhân, kết hợp hệ thống CMS quản trị nội dung đa ngôn ngữ bằng Laravel và FilamentPHP.

**EN:** A full-stack portfolio platform built to showcase projects, experience, and technical skills, powered by a multilingual content management system using Laravel and FilamentPHP.

#### Mô tả dài

**VI:** Phần lớn website portfolio cá nhân được xây dựng theo dạng tĩnh, khó mở rộng và khó quản lý nội dung khi số lượng dự án tăng lên.

DanCru Portfolio được xây dựng như một nền tảng portfolio có backend quản trị riêng, cho phép quản lý dự án, kinh nghiệm, kỹ năng và nội dung đa ngôn ngữ từ một dashboard tập trung mà không cần chỉnh sửa source code trực tiếp.

**EN:** Most personal portfolio websites are static and become difficult to maintain as the amount of content grows.

DanCru Portfolio was designed as a portfolio platform with a dedicated administration system, allowing projects, experience, skills, and multilingual content to be managed from a centralized dashboard without directly editing source code.

#### Nội dung chi tiết

**VI:** DanCru Portfolio không chỉ là website giới thiệu cá nhân mà được xây dựng như một hệ thống quản lý nội dung hoàn chỉnh.

Frontend được phát triển bằng React, TypeScript và Vite nhằm tối ưu hiệu năng tải trang và trải nghiệm người dùng. Phần giao diện sử dụng Tailwind CSS với hệ thống theme tùy chỉnh lấy cảm hứng từ phong cách UI của Valorant.

Backend sử dụng Laravel 11 kết hợp FilamentPHP để xây dựng dashboard quản trị nội dung. Hệ thống cho phép quản lý dự án, kinh nghiệm làm việc, kỹ năng, thông tin cá nhân và nội dung đa ngôn ngữ Việt - Anh thông qua giao diện quản trị trực quan.

Mục tiêu của dự án là tạo ra một nền tảng portfolio có khả năng mở rộng lâu dài thay vì một website tĩnh đơn giản, đồng thời đóng vai trò như trung tâm trình bày toàn bộ sản phẩm và hành trình phát triển cá nhân.

**EN:** DanCru Portfolio was built as more than a personal website — it functions as a complete content management platform.

The frontend was developed using React, TypeScript, and Vite to ensure fast performance and a modern user experience. The interface uses Tailwind CSS with a custom visual identity inspired by Valorant-style UI systems.

The backend is powered by Laravel 11 and FilamentPHP, providing a dedicated administration panel for managing projects, experience, skills, personal information, and bilingual content.

The goal was to create a scalable portfolio platform rather than a simple static website, serving as the central hub for showcasing professional work and technical growth.

#### Trách nhiệm

**VI:** Thiết kế kiến trúc frontend và backend cho toàn bộ hệ thống.
Xây dựng giao diện portfolio bằng React, TypeScript và Tailwind CSS.
Thiết kế theme tùy chỉnh lấy cảm hứng từ giao diện Valorant.
Xây dựng CMS quản trị nội dung bằng Laravel và FilamentPHP.
Phát triển hệ thống đa ngôn ngữ Việt - Anh.
Thiết kế cấu trúc dữ liệu cho dự án, kinh nghiệm và kỹ năng.
Tối ưu trải nghiệm người dùng, hiệu ứng chuyển động và khả năng responsive.
Triển khai và vận hành hệ thống production.

**EN:** Designed the overall frontend and backend architecture.
Built the portfolio interface using React, TypeScript, and Tailwind CSS.
Created a custom Valorant-inspired visual theme.
Developed a CMS dashboard using Laravel and FilamentPHP.
Implemented Vietnamese-English multilingual support.
Designed content structures for projects, experience, and skills.
Optimized responsiveness, animations, and user experience.
Managed deployment and production operations.

#### Tech stack

- React
- TypeScript
- Vite
- Tailwind CSS
- Laravel 11
- FilamentPHP v3
- MySQL
- REST API
- Multilingual System

#### Features

- **VI:** Portfolio đa ngôn ngữ Việt - Anh

**EN:** Vietnamese-English multilingual portfolio
- **VI:** Quản lý kinh nghiệm làm việc

**EN:** Experience management
- **VI:** Dashboard quản trị tập trung

**EN:** Centralized admin dashboard
- **VI:** Hệ thống API Laravel phục vụ frontend

**EN:** Laravel API backend

#### Metrics / Highlights

-   - **label:** **VI:** Full-stack Architecture

**EN:** Full-stack Architecture
  - **value:** **VI:** Frontend và backend được xây dựng tách biệt hoàn toàn.

**EN:** Fully separated frontend and backend architecture.
-   - **label:** **VI:** Multilingual CMS

**EN:** Multilingual CMS
  - **value:** **VI:** Hỗ trợ quản lý nội dung song ngữ Việt - Anh.

**EN:** Supports bilingual content management (Vietnamese and English).
-   - **label:** **VI:** Admin-driven Content

**EN:** Admin-driven Content
  - **value:** **VI:** Toàn bộ dữ liệu portfolio có thể quản lý từ dashboard.

**EN:** Portfolio content is fully managed through an admin dashboard.

#### Gallery images

- /uploads/portfolio/gallery/1FZZ1RWm8dZGDhO78yw2NSpnDSAx0gqxYWPKaprV.png

## 8. Chứng chỉ & Thành tích

### Sinh viên xuất sắc các kỳ & Thủ khoa đầu ra / Top student of each semester & Valedictorian of the graduating class

- **ID:** 1
- **Issuer:** Cao đẳng FPT Polytechnic / FPT Polytechnic College
- **Issue date:** 2024-05-20
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/mVrD0NfxQGbjPeMSYObRsjQj1I2ISjBWJDf2HgQT.jpg`
- **Sort order:** 1
- **Active:** 1
- **Created at:** 2026-02-14 09:15:22
- **Updated at:** 2026-05-30 01:10:08

### Bằng khen giỏi và xuất sắc 6 kỳ / Certificates of excellence and outstanding performance for 6 terms.

- **ID:** 2
- **Issuer:** Trường cao đẳng FPT Polytechnic / FPT Polytechnic College
- **Issue date:** 2025-10-15
- **URL:** grg
- **Image:** `/uploads/portfolio/oY7OgPe6lqvSUbZZDHLgX4O75LPwHzLYXEn5wn9g.jpg`
- **Sort order:** 2
- **Active:** 1
- **Created at:** 2026-02-14 13:44:44
- **Updated at:** 2026-02-15 03:35:08

### Giải khuyến khích cuộc thi AI4Life / Encouragement Award in the AI4Life Competition

- **ID:** 3
- **Issuer:** Trường cao đẳng FPT Polytechnic / FPT Polytechnic College
- **Issue date:** 2025-08-09
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/ZzkIJv4T1Sv6l5BBnTUE6ve35O3NVQ8l0aHTJNMj.jpg`
- **Sort order:** 3
- **Active:** 1
- **Created at:** 2026-02-15 03:36:46
- **Updated at:** 2026-02-15 03:37:12

### Hiến máu tình nguyện / Voluntary blood donation

- **ID:** 4
- **Issuer:** BCĐ vận động hiến máu tình nguyện tỉnh Thanh Hóa / Steering Committee for the Blood Donation Program of Thanh Hoa Province
- **Issue date:** 2025-04-10
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/PWzaaL19ApStStgU3iWEPmXQqEtm32w47mc0ZQXH.jpg`
- **Sort order:** 4
- **Active:** 1
- **Created at:** 2026-02-15 03:39:40
- **Updated at:** 2026-02-15 03:39:40

### TOP 20 HACKATHON FRONTEND MASTER 2024

- **ID:** 5
- **Issuer:** Hackathon x FPT
- **Issue date:** 2024-06-04
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/1z44bIPb5KpEUQlR5dqHOU5MVGjM5Y1I4ShH3Fga.jpg`
- **Sort order:** 5
- **Active:** 1
- **Created at:** 2026-02-15 03:41:15
- **Updated at:** 2026-02-15 03:41:15

### Bậc thầy săn bug / Bug slayer

- **ID:** 6
- **Issuer:** FPT  / FPT
- **Issue date:** 2025-04-08
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/j2yRgX4NEb6Lx7qx5NxuYlJzRo7n8fqxvqyI57Yn.jpg`
- **Sort order:** 6
- **Active:** 1
- **Created at:** 2026-02-15 03:42:45
- **Updated at:** 2026-02-15 03:42:45

### Giáo dục QP&AN / National Defense and Security Education

- **ID:** 7
- **Issuer:** Trung tâm giáo dục Quốc phòng và An ninh Trường Đại học Hồng Đức / Center for National Defense and Security Education, Hong Duc University
- **Issue date:** 2025-01-14
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/bBGS7NgWmBpEtZWwXghieyEoSYGc4j0c0X5PLiES.jpg`
- **Sort order:** 7
- **Active:** 1
- **Created at:** 2026-02-15 03:44:32
- **Updated at:** 2026-02-15 03:44:32

### Tình nguyện viên tại Giải Vô địch Quốc gia Việt  Nam VEX Robotics 2025 / Volunteers at the Vietnam National Robotics Championship VEX 2025

- **ID:** 8
- **Issuer:** Liên minh Thúc đẩy Giáo dục STEM / Alliance to Promote STEM Education
- **Issue date:** 2025-01-16
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/R0QZ3u7PKCa1CFt0zXbC79MFPEXOP91rZ4alNqEU.png`
- **Sort order:** 8
- **Active:** 1
- **Created at:** 2026-02-15 03:48:04
- **Updated at:** 2026-02-15 03:48:04

### Kỹ năng lập trình PHP / PHP programming skills

- **ID:** 9
- **Issuer:** FPT
- **Issue date:** 2024-08-18
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/OsGgIi2mC7exmGKQMp5fw3PyjgVPbgIfknBi5EHq.png`
- **Sort order:** 9
- **Active:** 1
- **Created at:** 2026-02-15 03:50:17
- **Updated at:** 2026-02-15 03:50:17

### Trọng tài Trưởng Cuộc thi Robot VEX IQ (VIQRC) năm 2024-2025 / Head Referee of the VEX IQ Robotics Competition (VIQRC) 2024-2025

- **ID:** 10
- **Issuer:** REC Foundation
- **Issue date:** 2025-01-08
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/pfS2cAU2t8rJpeSN8m6sNId6Qj7LC4sTQxdWGhQ2.png`
- **Sort order:** 10
- **Active:** 1
- **Created at:** 2026-02-15 03:53:56
- **Updated at:** 2026-02-15 03:53:56

### Gemini Certified Student

- **ID:** 11
- **Issuer:** Google for Education
- **Issue date:** 2026-02-15
- **URL:** Không có dữ liệu
- **Image:** `/uploads/portfolio/gLqj3sSgQWsFwSCD2Iqt7aF2P02R4i45wsbU8c8K.png`
- **Sort order:** 11
- **Active:** 1
- **Created at:** 2026-05-03 16:26:11
- **Updated at:** 2026-05-30 01:08:15

## 9. Bản dịch / Translations

_Bảng `translations` có schema nhưng không có dữ liệu INSERT trong file dump._

## 10. Tin nhắn liên hệ

Bảng này chứa dữ liệu liên hệ từ người dùng. Email được che một phần để tránh lộ dữ liệu cá nhân trong tài liệu chia sẻ.

### Message #1: project

- **Name:** Anh Đức
- **Email:** ad***@thuyhm.code
- **Subject:** project
- **Is read:** 1
- **Created at:** 2026-02-14 02:03:34
- **Updated at:** 2026-02-14 02:05:09

#### Message

rrrrr

### Message #2: project

- **Name:** Tao
- **Email:** da***@gmail.com
- **Subject:** project
- **Is read:** 1
- **Created at:** 2026-02-14 13:25:43
- **Updated at:** 2026-04-19 04:22:32

#### Message

Mày là aiii

### Message #3: other

- **Name:** Hfhdh
- **Email:** ng***@gmail.com
- **Subject:** other
- **Is read:** 1
- **Created at:** 2026-02-14 13:53:05
- **Updated at:** 2026-04-19 04:22:31

#### Message

Bdbdh

### Message #4: other

- **Name:** Teatstst
- **Email:** ng***@gmail.com
- **Subject:** other
- **Is read:** 1
- **Created at:** 2026-02-14 14:00:03
- **Updated at:** 2026-02-14 14:02:09

#### Message

Bdbd

### Message #5: project

- **Name:** Nguyễn Linh
- **Email:** li***@gmail.com
- **Subject:** project
- **Is read:** 1
- **Created at:** 2026-03-19 00:34:25
- **Updated at:** 2026-04-19 04:22:23

#### Message

Alo ajinomoto

### Message #9: other

- **Name:** Nguyễn Anh Đức
- **Email:** ad***@thuyhm.com
- **Subject:** other
- **Is read:** 1
- **Created at:** 2026-05-30 03:44:48
- **Updated at:** 2026-05-30 04:01:32

#### Message

Bạn có đẹp trai không


## 11. Tài liệu cấu trúc database

### Table `cache`

- **Số cột:** 3
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| key | varchar(255) NOT NULL |
| value | mediumtext NOT NULL |
| expiration | int(11) NOT NULL |

### Table `cache_locks`

- **Số cột:** 3
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| key | varchar(255) NOT NULL |
| owner | varchar(255) NOT NULL |
| expiration | int(11) NOT NULL |

### Table `certifications`

- **Số cột:** 10
- **Số dòng dữ liệu trong dump:** 11

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| name | varchar(255) NOT NULL |
| issuer | varchar(255) NOT NULL |
| issue_date | date DEFAULT NULL |
| url | varchar(255) DEFAULT NULL |
| image | varchar(255) DEFAULT NULL |
| sort_order | int(11) NOT NULL DEFAULT 0 |
| is_active | tinyint(1) NOT NULL DEFAULT 1 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `contact_messages`

- **Số cột:** 8
- **Số dòng dữ liệu trong dump:** 6

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| name | varchar(255) NOT NULL |
| email | varchar(255) NOT NULL |
| subject | varchar(255) NOT NULL |
| message | text NOT NULL |
| is_read | tinyint(1) NOT NULL DEFAULT 0 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `educations`

- **Số cột:** 11
- **Số dòng dữ liệu trong dump:** 2

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| degree | varchar(255) NOT NULL |
| school | varchar(255) NOT NULL |
| period | varchar(255) NOT NULL |
| gpa | varchar(255) DEFAULT NULL |
| description | text DEFAULT NULL |
| image | varchar(255) DEFAULT NULL |
| sort_order | int(11) NOT NULL DEFAULT 0 |
| is_active | tinyint(1) NOT NULL DEFAULT 1 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `experiences`

- **Số cột:** 13
- **Số dòng dữ liệu trong dump:** 5

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| position | varchar(255) NOT NULL |
| company | varchar(255) NOT NULL |
| location | varchar(255) DEFAULT NULL |
| period | varchar(255) NOT NULL |
| description | text DEFAULT NULL |
| achievements | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`achievements`)) |
| technologies | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`technologies`)) |
| rank | varchar(255) DEFAULT NULL |
| sort_order | int(11) NOT NULL DEFAULT 0 |
| is_active | tinyint(1) NOT NULL DEFAULT 1 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `failed_jobs`

- **Số cột:** 7
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| uuid | varchar(255) NOT NULL |
| connection | text NOT NULL |
| queue | text NOT NULL |
| payload | longtext NOT NULL |
| exception | longtext NOT NULL |
| failed_at | timestamp NOT NULL DEFAULT current_timestamp() |

### Table `job_batches`

- **Số cột:** 10
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| id | varchar(255) NOT NULL |
| name | varchar(255) NOT NULL |
| total_jobs | int(11) NOT NULL |
| pending_jobs | int(11) NOT NULL |
| failed_jobs | int(11) NOT NULL |
| failed_job_ids | longtext NOT NULL |
| options | mediumtext DEFAULT NULL |
| cancelled_at | int(11) DEFAULT NULL |
| created_at | int(11) NOT NULL |
| finished_at | int(11) DEFAULT NULL |

### Table `jobs`

- **Số cột:** 7
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| queue | varchar(255) NOT NULL |
| payload | longtext NOT NULL |
| attempts | tinyint(3) UNSIGNED NOT NULL |
| reserved_at | int(10) UNSIGNED DEFAULT NULL |
| available_at | int(10) UNSIGNED NOT NULL |
| created_at | int(10) UNSIGNED NOT NULL |

### Table `migrations`

- **Số cột:** 3
- **Số dòng dữ liệu trong dump:** 14

| Column | Definition |
| --- | --- |
| id | int(10) UNSIGNED NOT NULL |
| migration | varchar(255) NOT NULL |
| batch | int(11) NOT NULL |

### Table `password_reset_tokens`

- **Số cột:** 3
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| email | varchar(255) NOT NULL |
| token | varchar(255) NOT NULL |
| created_at | timestamp NULL DEFAULT NULL |

> Ghi chú: Bảng này có thể chứa dữ liệu xác thực/phiên đăng nhập. Tài liệu chỉ mô tả cấu trúc, không copy dữ liệu nhạy cảm.

### Table `personal_access_tokens`

- **Số cột:** 10
- **Số dòng dữ liệu trong dump:** 2

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| tokenable_type | varchar(255) NOT NULL |
| tokenable_id | bigint(20) UNSIGNED NOT NULL |
| name | text NOT NULL |
| token | varchar(64) NOT NULL |
| abilities | text DEFAULT NULL |
| last_used_at | timestamp NULL DEFAULT NULL |
| expires_at | timestamp NULL DEFAULT NULL |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

> Ghi chú: Bảng này có thể chứa dữ liệu xác thực/phiên đăng nhập. Tài liệu chỉ mô tả cấu trúc, không copy dữ liệu nhạy cảm.

### Table `portfolio_settings`

- **Số cột:** 7
- **Số dòng dữ liệu trong dump:** 16

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| key | varchar(255) NOT NULL |
| value | text DEFAULT NULL |
| type | varchar(255) NOT NULL DEFAULT 'text' |
| group | varchar(255) NOT NULL DEFAULT 'general' |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `projects`

- **Số cột:** 25
- **Số dòng dữ liệu trong dump:** 4

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| title | varchar(255) NOT NULL |
| slug | varchar(255) NOT NULL |
| category | varchar(255) DEFAULT NULL |
| description | text DEFAULT NULL |
| long_description | longtext DEFAULT NULL |
| content | longtext DEFAULT NULL |
| role | text DEFAULT NULL |
| responsibilities | text DEFAULT NULL |
| image | varchar(255) DEFAULT NULL |
| gallery_images | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`gallery_images`)) |
| tech_stack | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tech_stack`)) |
| features | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`features`)) |
| metrics | longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metrics`)) |
| duration | varchar(255) DEFAULT NULL |
| team | varchar(255) DEFAULT NULL |
| status | varchar(255) NOT NULL DEFAULT 'Completed' |
| start_date | date DEFAULT NULL |
| end_date | date DEFAULT NULL |
| live_url | varchar(255) DEFAULT NULL |
| github_url | varchar(255) DEFAULT NULL |
| sort_order | int(11) NOT NULL DEFAULT 0 |
| is_active | tinyint(1) NOT NULL DEFAULT 1 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `sessions`

- **Số cột:** 6
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| id | varchar(255) NOT NULL |
| user_id | bigint(20) UNSIGNED DEFAULT NULL |
| ip_address | varchar(45) DEFAULT NULL |
| user_agent | text DEFAULT NULL |
| payload | longtext NOT NULL |
| last_activity | int(11) NOT NULL |

> Ghi chú: Bảng này có thể chứa dữ liệu xác thực/phiên đăng nhập. Tài liệu chỉ mô tả cấu trúc, không copy dữ liệu nhạy cảm.

### Table `skills`

- **Số cột:** 10
- **Số dòng dữ liệu trong dump:** 14

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| name | varchar(255) NOT NULL |
| category | varchar(255) NOT NULL |
| proficiency | int(11) NOT NULL DEFAULT 0 |
| icon | varchar(255) DEFAULT NULL |
| icon_url | varchar(255) DEFAULT NULL |
| sort_order | int(11) NOT NULL DEFAULT 0 |
| is_active | tinyint(1) NOT NULL DEFAULT 1 |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `translations`

- **Số cột:** 6
- **Số dòng dữ liệu trong dump:** 0

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| key | varchar(255) NOT NULL |
| locale | varchar(255) NOT NULL |
| value | text DEFAULT NULL |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

### Table `users`

- **Số cột:** 9
- **Số dòng dữ liệu trong dump:** 1

| Column | Definition |
| --- | --- |
| id | bigint(20) UNSIGNED NOT NULL |
| name | varchar(255) NOT NULL |
| email | varchar(255) NOT NULL |
| role | enum('user','admin') NOT NULL DEFAULT 'user' |
| email_verified_at | timestamp NULL DEFAULT NULL |
| password | varchar(255) NOT NULL |
| remember_token | varchar(100) DEFAULT NULL |
| created_at | timestamp NULL DEFAULT NULL |
| updated_at | timestamp NULL DEFAULT NULL |

> Ghi chú: Bảng này có thể chứa dữ liệu xác thực/phiên đăng nhập. Tài liệu chỉ mô tả cấu trúc, không copy dữ liệu nhạy cảm.

## 12. Phụ lục nội dung raw đã chuẩn hóa

Phụ lục này giữ lại dữ liệu đã parse theo dạng key-value để dễ đối chiếu với database. Các bảng nhạy cảm vẫn được lược bỏ giá trị bí mật.

### Raw table `portfolio_settings`

#### Row #1

- **id:**
  1
- **key:**
  hero_title
- **value:**

  **VI:** Lập trình viên

  **EN:** Web Developer
- **type:**
  text
- **group:**
  hero
- **created_at:**
  2026-02-10 10:59:05
- **updated_at:**
  2026-02-14 09:39:24

#### Row #2

- **id:**
  2
- **key:**
  hero_subtitle
- **value:**

  **VI:** Sinh viên năm 3 ngành CNTT, đam mê xây dựng web app, tool và xây dựng sản phẩm thực tế, ứng dụng cao.

  **EN:** A third-year IT student passionate about building web apps, tools, and developing practical, high-application products.
- **type:**
  text
- **group:**
  hero
- **created_at:**
  2026-02-10 10:59:05
- **updated_at:**
  2026-05-30 01:27:11

#### Row #3

- **id:**
  3
- **key:**
  about_name
- **value:**
  Nguyễn Anh Đức
- **type:**
  text
- **group:**
  about
- **created_at:**
  2026-02-10 10:59:05
- **updated_at:**
  2026-02-10 10:59:05

#### Row #4

- **id:**
  4
- **key:**
  about_description
- **value:**
  Tôi là sinh viên năm 3 ngành Công nghệ thông tin với niềm đam mê mãnh liệt về lập trình.
- **type:**
  text
- **group:**
  about
- **created_at:**
  2026-02-10 10:59:05
- **updated_at:**
  2026-02-10 10:59:05

#### Row #5

- **id:**
  5
- **key:**
  contact_email
- **value:**
  nguyenanhduc@example.com
- **type:**
  text
- **group:**
  contact
- **created_at:**
  2026-02-10 10:59:05
- **updated_at:**
  2026-02-10 10:59:05

#### Row #6

- **id:**
  6
- **key:**
  additional_skills
- **value:**

  **VI:** Giao tiếp, Làm việc nhóm, Quản lý thời gian, Tự học, Phát triển bản thân, Thích nghi

  **EN:** Communication, Teamwork, Time Management, Self-Learning, Personal Development, Adaptability
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-02-14 09:13:18
- **updated_at:**
  2026-05-30 01:26:28

#### Row #9

- **id:**
  9
- **key:**
  core_value_1_title
- **value:**

  **VI:** Mọi thứ trên đời đều chỉ là trải nghiệm

  **EN:** Everything in life is just an experience.
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-04-29 23:38:09
- **updated_at:**
  2026-04-29 23:38:09

#### Row #10

- **id:**
  10
- **key:**
  core_value_1_desc
- **value:**

  **VI:** Mọi thứ trên đời đều chỉ là trải nghiệm.

  **EN:** Everything in life is just an experience.
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-04-29 23:42:13
- **updated_at:**
  2026-04-30 00:40:23

#### Row #11

- **id:**
  11
- **key:**
  core_value_2_desc
- **value:**

  **VI:** Nếu bạn không gặp khó khăn, tức là bạn đang đứng yên.

  **EN:** If you're not having any difficulties, it means you're standing still.
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-04-30 00:40:23
- **updated_at:**
  2026-04-30 00:40:23

#### Row #12

- **id:**
  12
- **key:**
  resume_url
- **value:**
  /uploads/portfolio/files/sBiBoXAVGAKXaUlWqBeqwFe2VDpSsyBA66NOke1i.pdf
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-04-30 01:26:06
- **updated_at:**
  2026-05-29 11:46:05

#### Row #13

- **id:**
  13
- **key:**
  core_value_3_desc
- **value:**

  **VI:** Càng nỗ lực, càng may mắn.

  **EN:** The effort you try, the lucky you are.
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 01:20:52
- **updated_at:**
  2026-05-30 01:20:52

#### Row #14

- **id:**
  14
- **key:**
  resume_ats_url
- **value:**
  /uploads/portfolio/files/VWWeP1g2enweOCCguUoaz2dDrVYszLksflYbBcq2.pdf
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 01:38:41
- **updated_at:**
  2026-05-30 01:38:41

#### Row #15

- **id:**
  15
- **key:**
  social_github
- **value:**
  https://github.com/dancru299
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 03:44:01
- **updated_at:**
  2026-05-30 03:44:01

#### Row #16

- **id:**
  16
- **key:**
  social_linkedin
- **value:**
  https://www.linkedin.com/in/dancru299/
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 03:44:01
- **updated_at:**
  2026-05-30 03:44:01

#### Row #17

- **id:**
  17
- **key:**
  social_facebook
- **value:**
  https://www.facebook.com/
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 03:44:01
- **updated_at:**
  2026-05-30 03:44:01

#### Row #18

- **id:**
  18
- **key:**
  social_youtube
- **value:**
  https://www.youtube.com/@ducdidauday299
- **type:**
  text
- **group:**
  general
- **created_at:**
  2026-05-30 03:44:01
- **updated_at:**
  2026-05-30 03:44:01

### Raw table `educations`

#### Row #1

- **id:**
  1
- **degree:**

  **VI:** Cử nhân thực hành ngành Phát triển Web

  **EN:** Bachelor of Practice in Web Development
- **school:**

  **VI:** Cao đẳng FPT Polytechnic (FPL)

  **EN:** FPT Polytechnic College
- **period:**
  2023 - 2025
- **gpa:**
  Valedictorian • GPA 3.81/4.0
- **description:**

  **VI:** Xây dựng nền tảng về phát triển Web, tư duy sản phẩm và kỹ năng làm việc nhóm.

  **EN:** Built a strong foundation in web development, product thinking, and teamwork.
- **image:**
  /uploads/portfolio/bMlJbltYrKf2rn65irQblNgTGJgH0O7zBG11QRD3.jpg
- **sort_order:**
  1
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-05-30 01:05:41

#### Row #3

- **id:**
  3
- **degree:**

  **VI:** Kỹ sư Công nghệ Thông tin

  **EN:** Engineer in Information Technology
- **school:**

  **VI:** Học viện Công nghệ Bưu chính Viễn thông (PTIT)

  **EN:** Posts and Telecommunications Institute of Technology (PTIT)
- **period:**
  2026 - 2030
- **gpa:**
  _Không có dữ liệu_
- **description:**

  **VI:** Theo học chương trình Kỹ sư CNTT nhằm mở rộng nền tảng học thuật và chuyên môn dài hạn.

  **EN:** Pursuing an IT engineering program to strengthen my academic and long-term technical foundation.
- **image:**
  /uploads/portfolio/7bthH7QVkvH2IbeQJZpXuVfA2f9KjPhmGsmLPcKn.jpg
- **sort_order:**
  2
- **is_active:**
  1
- **created_at:**
  2026-05-30 00:17:27
- **updated_at:**
  2026-05-30 01:04:48

### Raw table `experiences`

#### Row #2

- **id:**
  2
- **position:**

  **VI:** Thực tập sinh Fullstack

  **EN:** Fullstack Web Developer Intern
- **company:**

  **VI:** Cty Cổ phẩn ThinkLabs

  **EN:** ThinkLabs Joint Stock Company
- **location:**

  **VI:** Thanh Hóa

  **EN:** Thanh Hoa - VietNam
- **period:**
  05/2025 - 04/2026
- **description:**

  **VI:** Tham gia phát triển các ứng dụng web và hệ thống quản lý doanh nghiệp trong môi trường thực tế. Làm việc với frontend, backend và cơ sở dữ liệu để triển khai các tính năng phục vụ người dùng.

  **EN:** Contributed to the development of web applications and enterprise management systems. Worked across frontend, backend, and database layers to deliver business features and improve user experience.
- **achievements:**

  **VI:** ['Tham gia phát triển hệ thống ERP và quản lý nhân sự cho doanh nghiệp', 'Xây dựng giao diện quản trị bằng React và Ant Design', 'Phát triển API bằng Node.js và làm việc với MongoDB', 'Tham gia phân tích yêu cầu và xử lý lỗi trong quá trình phát triển sản phẩm']

  **EN:** ['Participate in developing ERP and human resource management systems for businesses.', 'Build admin interfaces using React and Ant Design.', 'Develop APIs using Node.js and work with MongoDB.', 'Participate in requirements analysis and bug fixing during product development.']
- **technologies:**

  - React
  - Node.js
  - Java
  - MongoDB
  - REST API
  - Microservice
- **rank:**
  Intern
- **sort_order:**
  3
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-05-29 14:41:32

#### Row #3

- **id:**
  3
- **position:**

  **VI:** Giảng viên Lập trình & Robotics

  **EN:** Programming & Robotics Instructor
- **company:**

  **VI:** Trung tâm sáng tạo công nghệ 8BIT

  **EN:** 8-BIT Technology Innovation Center
- **location:**

  **VI:** Thanh Hóa

  **EN:** Thanh Hoa - VietNam
- **period:**
  09/2025 - 04/2026
- **description:**

  **VI:** Giảng dạy lập trình và robotics cho học sinh tiểu học và THCS thông qua các môn học như Scratch, Python và Robotics. Đồng thời tham gia xây dựng giáo trình, thiết kế bài giảng và hỗ trợ các hoạt động giáo dục công nghệ tại trung tâm.

  **EN:** Taught programming and robotics to elementary and middle school students through courses such as Scratch, Python, and Robotics. Also contributed to curriculum development, lesson planning, and educational technology activities.
- **achievements:**

  **VI:** ['Đạt danh hiệu Nhân viên Part-time Xuất sắc nhất', 'Đạt thành tích doanh thu cao nhất trong nhóm nhân sự Part-time', 'Tham gia phát triển hệ thống LMS phục vụ hoạt động đào tạo của trung tâm', 'Thiết kế và giảng dạy các khóa học Scratch, Python và Robotics cho học sinh', 'Hỗ trợ xây dựng tài liệu và lộ trình học tập phù hợp với từng độ tuổi']

  **EN:** ['Recognized as Outstanding Part-time Employee', 'Achieved the highest revenue performance among part-time staff', "Contributed to the development of the center's Learning Management System (LMS)", 'Designed and delivered Scratch, Python, and Robotics courses for students', 'Supported curriculum and learning roadmap development for different age groups']
- **technologies:**

  - Python
  - Scratch
  - Robotics
  - STEM Education
  - Curriculum Design
  - Classroom Management
  - Public Speaking
- **rank:**
  Giảng viên
- **sort_order:**
  4
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-05-29 14:46:29

#### Row #4

- **id:**
  4
- **position:**

  **VI:** Software Developer (Independent Projects)

  **EN:** Software Developer (Independent Projects)
- **company:**

  **VI:** Dự án cá nhân & Cộng tác bên ngoài

  **EN:** Independent & Collaborative Projects
- **location:**

  **VI:** Tại nhà

  **EN:** At home
- **period:**
  2024 - Đến nay
- **description:**

  **VI:** Chủ động tham gia các dự án phần mềm ngoài phạm vi học tập và công việc chính nhằm tích lũy kinh nghiệm thực tế. Tham gia vào nhiều giai đoạn phát triển sản phẩm từ phân tích yêu cầu, phát triển tính năng đến triển khai và vận hành.

  **EN:** Actively contributed to software projects beyond academic and primary work responsibilities to gain real-world experience. Involved in various stages of product development, from requirements analysis and feature implementation to deployment and maintenance.
- **achievements:**

  **VI:** ['Tham gia phát triển nhiều dự án web và hệ thống quản lý thực tế', 'Làm việc với cả Frontend, Backend và cơ sở dữ liệu', 'Tiếp cận quy trình phát triển phần mềm trong môi trường cộng tác', 'Tự nghiên cứu và áp dụng công nghệ mới vào dự án', 'Xây dựng kinh nghiệm thực chiến ngoài chương trình đào tạo chính quy']

  **EN:** ['Contributed to multiple real-world web applications and management systems', 'Worked across frontend, backend, and database development', 'Collaborated within real software development workflows', 'Researched and applied new technologies to project requirements', 'Built practical engineering experience beyond formal education']
- **technologies:**

  - React
  - Next.js
  - Node.js
  - TypeScript
  - Laravel
  - MongoDB
  - MySQL
  - Git
  - Python
  - REST API
- **rank:**
  Trung cấp
- **sort_order:**
  2
- **is_active:**
  1
- **created_at:**
  2026-02-14 11:10:45
- **updated_at:**
  2026-05-29 14:14:05

#### Row #5

- **id:**
  5
- **position:**

  **VI:** Sinh viên ngành Công nghệ Thông tin

  **EN:** Software Engineering Student
- **company:**

  **VI:** Học viện Công nghệ Bưu chính Viễn thông (PTIT)

  **EN:** Posts and Telecommunications Institute of Technology (PTIT)
- **location:**

  **VI:** Học từ xa

  **EN:** Remote Learning
- **period:**
  01/2026-2030
- **description:**

  **VI:** Theo học chương trình đại học ngành Công nghệ Thông tin theo hình thức từ xa nhằm nâng cao nền tảng học thuật, kiến thức chuyên sâu về khoa học máy tính và kỹ thuật phần mềm, đồng thời duy trì công việc thực tế trong ngành.

  **EN:** Pursuing a Bachelor's degree in Information Technology through a remote learning program while continuing professional work experience in software development.
- **achievements:**

  **VI:** ['Tiếp tục theo đuổi chương trình đại học ngành Công nghệ Thông tin', 'Kết hợp học tập học thuật với kinh nghiệm thực tế trong ngành phần mềm', 'Mở rộng kiến thức về khoa học máy tính, hệ thống và kỹ thuật phần mềm', 'Xây dựng nền tảng dài hạn cho định hướng Software Engineer']

  **EN:** ["Pursuing a Bachelor's degree in Information Technology", 'Combining academic studies with hands-on industry experience', 'Expanding knowledge in computer science, systems, and software engineering', 'Building a strong foundation for a long-term software engineering career']
- **technologies:**

  - Computer Science
  - Software Engineering
  - Information Systems
  - Algorithms
  - Databases
- **rank:**
  Bachelor's Degree
- **sort_order:**
  5
- **is_active:**
  1
- **created_at:**
  2026-02-14 11:15:53
- **updated_at:**
  2026-05-29 14:52:13

#### Row #6

- **id:**
  6
- **position:**

  **VI:** Học viên - Chương trình Đào tạo Nhân tài AI Thực chiến

  **EN:** Trainee - Vingroup Practical AI Talent Development Program
- **company:**

  **VI:** Tập đoàn Vingroup (phối hợp VinUniversity)

  **EN:** Vingroup Corporation (in collaboration with VinUniversity)
- **location:**

  **VI:** Hà Nội (VinUni - Vinhomes Ocean Park, Gia Lâm)

  **EN:** Hanoi, Vietnam (VinUniversity Campus, Vinhomes Ocean Park)
- **period:**
  Tháng 4/2026 - Tháng 7/2026 (12 tuần)
- **description:**

  **VI:** Tham gia chương trình đào tạo AI thực chiến 12 tuần toàn thời gian của Tập đoàn Vingroup (phối hợp VinUni). Chương trình theo mô hình 3+3+6: 3 tuần nền tảng, 3 tuần mô phỏng thực chiến và 6 tuần làm dự án thực tế tại doanh nghiệp thuộc hệ sinh thái Vingroup. Tập trung phát triển kỹ năng AI ứng dụng, tư duy sản phẩm và làm việc trực tiếp với mentor là chuyên gia dự án AI.

  **EN:** Participated in Vingroup's 12-week full-time Practical AI Talent Development Program (Foundation Level), implemented in collaboration with VinUniversity. Structured in 3+3+6 model: 3 weeks foundational training, 3 weeks simulated real-world scenarios, and 6 weeks hands-on project work at Vingroup ecosystem companies. Focused on applied AI skills, product thinking, and real business impact under mentorship of industry AI project managers.
- **achievements:**

  **VI:** ['Hoàn thành chương trình đào tạo AI thực chiến toàn thời gian kéo dài 12 tuần theo mô hình 3+3+6 của Vingroup và VinUniversity', 'Xây dựng các giải pháp AI ứng dụng sử dụng LLM, RAG, AI Agents và MLOps cho các bài toán doanh nghiệp mô phỏng và thực tế', 'Thực hiện dự án AI theo nhóm dưới sự hướng dẫn trực tiếp của chuyên gia ngành, áp dụng quy trình phát triển sản phẩm AI từ ý tưởng đến triển khai', 'Đạt chuẩn năng lực theo khung SFIA thông qua các bài đánh giá kỹ năng kỹ thuật, tư duy sản phẩm và năng lực làm việc dự án']

  **EN:** ["Completed Vingroup's competitive 12-week full-time Practical AI Talent Development Program", 'Developed AI applications using Python, LLMs, RAG pipelines, AI Agents, and MLOps workflows', 'Worked on real-world business use cases within the Vingroup ecosystem under direct mentorship from AI industry practitioners', 'Demonstrated competencies aligned with the SFIA framework in software engineering, AI development, and product thinking']
- **technologies:**

  - Python
  - OpenAI API
  - LangGraph
  - AI Agents
  - Software Testing
  - Playwright
  - Pytest
  - Docker
  - GitHub Actions
  - MLOps
- **rank:**
  Trainee
- **sort_order:**
  6
- **is_active:**
  1
- **created_at:**
  2026-05-03 16:14:40
- **updated_at:**
  2026-05-30 01:17:09

### Raw table `skills`

#### Row #1

- **id:**
  1
- **name:**
  React/Next.js
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  90
- **icon:**
  Cpu
- **icon_url:**
  /storage/portfolio/icons/9jk0MonUA1pSf7llharXYZwXnhYGSqdOnbkjFM06.png
- **sort_order:**
  1
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:20:08

#### Row #2

- **id:**
  2
- **name:**
  Vue.js
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  85
- **icon:**
  Cpu
- **icon_url:**
  /storage/portfolio/icons/GnftYD7PctDEQu5QIEK0ge64DRAwh7QeuQXaun6x.png
- **sort_order:**
  2
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:20:21

#### Row #3

- **id:**
  3
- **name:**
  TypeScript
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  88
- **icon:**
  Cpu
- **icon_url:**
  /storage/portfolio/icons/hdt6iPnvdluWWViYftjwZ1vyOk8eODiKCC9bp1UH.png
- **sort_order:**
  3
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:20:32

#### Row #4

- **id:**
  4
- **name:**
  Tailwind CSS
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  95
- **icon:**
  Cpu
- **icon_url:**
  /storage/portfolio/icons/KXURTGx5KHgmmdiSD3z1ELvagvlRchmgt0jUINg9.png
- **sort_order:**
  4
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:20:45

#### Row #5

- **id:**
  5
- **name:**
  Node.js
- **category:**

  **VI:** Backend

  **EN:** Backend
- **proficiency:**
  85
- **icon:**
  Server
- **icon_url:**
  /storage/portfolio/icons/nNh4JPstNh2P4NLMZOYW7hE8ZxC8uPUeT97aN28h.png
- **sort_order:**
  5
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:48:46

#### Row #6

- **id:**
  6
- **name:**
  Php
- **category:**

  **VI:** Backend

  **EN:** Backend
- **proficiency:**
  70
- **icon:**
  Server
- **icon_url:**
  /storage/portfolio/icons/gRWu5PQSXH8NX7v56Fa41wUZzd0j4ewaUpvMCcmn.png
- **sort_order:**
  6
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 14:42:49

#### Row #7

- **id:**
  7
- **name:**
  Laravel/PHP
- **category:**

  **VI:** Backend

  **EN:** Backend
- **proficiency:**
  75
- **icon:**
  Server
- **icon_url:**
  /storage/portfolio/icons/9fOZlvg8ejitlUkhVhDOyiKLltilNJlsz0RerJMl.png
- **sort_order:**
  7
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:49:01

#### Row #8

- **id:**
  8
- **name:**
  Javascript
- **category:**

  **VI:** Backend

  **EN:** Backend
- **proficiency:**
  85
- **icon:**
  Server
- **icon_url:**
  /storage/portfolio/icons/D1E9VdCw2AVNvacxmgYzgztSxdL7jX5vzonY8Oyr.jpg
- **sort_order:**
  8
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:49:45

#### Row #10

- **id:**
  10
- **name:**
  MongoDB
- **category:**

  **VI:** Cơ sở dữ liệu

  **EN:** Database
- **proficiency:**
  85
- **icon:**
  Database
- **icon_url:**
  /storage/portfolio/icons/QiyabGT7ovh6C4L35Wi1ewAWgdbKtLRy8VCSFCGs.jpg
- **sort_order:**
  10
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:10:14

#### Row #12

- **id:**
  12
- **name:**
  MySQL
- **category:**

  **VI:** Cơ sở dữ liệu

  **EN:** Database
- **proficiency:**
  85
- **icon:**
  Database
- **icon_url:**
  /storage/portfolio/icons/rNQo1DjilVAKgxQC4dGk6XoqdC1FMQVKFkaifl7L.png
- **sort_order:**
  12
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:04:59
- **updated_at:**
  2026-02-14 10:10:42

#### Row #17

- **id:**
  17
- **name:**
  HTML/CSS
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  0
- **icon:**
  _Không có dữ liệu_
- **icon_url:**
  /storage/portfolio/icons/X1iEv5EXR5jV2P72I8FYFNwm66vPfE9rNyCh6Swj.png
- **sort_order:**
  11
- **is_active:**
  1
- **created_at:**
  2026-02-14 10:41:19
- **updated_at:**
  2026-02-14 10:41:19

#### Row #18

- **id:**
  18
- **name:**
  JavaScript
- **category:**

  **VI:** Frontend

  **EN:** Frontend
- **proficiency:**
  0
- **icon:**
  _Không có dữ liệu_
- **icon_url:**
  /storage/portfolio/icons/uEVQUUMWZ2ql7MNhevoZKI03pVyGp5mrNsDotGPf.jpg
- **sort_order:**
  12
- **is_active:**
  1
- **created_at:**
  2026-02-14 10:42:32
- **updated_at:**
  2026-02-14 10:42:32

#### Row #19

- **id:**
  19
- **name:**
  Python
- **category:**

  **VI:** Backend

  **EN:** Backend
- **proficiency:**
  0
- **icon:**
  _Không có dữ liệu_
- **icon_url:**
  /uploads/portfolio/icons/9DMPl8klfnzlyQO5WjyQUMeBU8Yl8X1kRClVqFS7.png
- **sort_order:**
  13
- **is_active:**
  1
- **created_at:**
  2026-02-14 14:43:13
- **updated_at:**
  2026-02-14 14:43:13

#### Row #20

- **id:**
  20
- **name:**
  PostgreSQL
- **category:**

  **VI:** Cơ sở dữ liệu

  **EN:** Database
- **proficiency:**
  0
- **icon:**
  _Không có dữ liệu_
- **icon_url:**
  /uploads/portfolio/icons/7YAooghZqnma6lVGTuhR0N7JymhfO4GhXEFwsfVJ.png
- **sort_order:**
  14
- **is_active:**
  1
- **created_at:**
  2026-05-30 01:24:47
- **updated_at:**
  2026-05-30 01:25:10

### Raw table `projects`

#### Row #1

- **id:**
  1
- **title:**

  **VI:** LavishStay - Nền tảng quản lý và đặt phòng khách sạn

  **EN:** LavishStay - Hospitality Booking & Management Platform
- **slug:**

  **VI:** h

  **EN:** h
- **category:**

  **VI:** Dự án tốt nghiệp

  **EN:** Graduation Project
- **description:**

  **VI:** Hệ thống quản lý & đặt phòng khách sạn trực tuyến

  **EN:** Online hotel management and booking system
- **long_description:**

  **VI:** Trong nhiều mô hình khách sạn và homestay lớn, quy trình quản lý phòng, đặt phòng và theo dõi khách hàng thường được thực hiện thủ công hoặc phân tán trên nhiều công cụ khác nhau.

  LavishStay được xây dựng nhằm số hóa quy trình vận hành lưu trú, giúp quản lý thông tin phòng, khách hàng, trạng thái đặt phòng và dữ liệu giao dịch trên một hệ thống tập trung.

  **EN:** Many big hotels and homestays still rely on manual processes or disconnected tools for room management and reservation tracking.

  LavishStay was developed to digitize hospitality operations by centralizing room management, customer information, booking status, and transaction workflows into a single platform.
- **content:**

  **VI:** LavishStay là dự án tốt nghiệp được xây dựng nhằm mô phỏng và triển khai thực tế các quy trình vận hành của hệ thống khách sạn và lưu trú hiện đại.

  Hệ thống cho phép khách hàng tìm kiếm và đặt phòng trực tuyến, trong khi phía quản trị có thể quản lý phòng, trạng thái đặt phòng, thông tin khách hàng và dữ liệu vận hành trên một dashboard tập trung.

  Phần trọng tâm của dự án nằm ở việc xây dựng backend với kiến trúc API phục vụ nhiều nhóm chức năng khác nhau, đảm bảo khả năng mở rộng, quản lý dữ liệu tập trung và hỗ trợ tích hợp frontend một cách linh hoạt.

  **EN:** LavishStay is a graduation project designed to simulate and implement real-world hospitality management workflows.

  The platform allows customers to browse and book rooms online, while administrators can manage rooms, reservation statuses, customer information, and operational data through a centralized dashboard.

  The main focus of the project was backend development, including API architecture, database design, business workflow implementation, and scalable system integration.
- **role:**

  **VI:** Trưởng nhóm & Backend Developer

  **EN:** Leader & Backend Developer
- **responsibilities:**

  **VI:** Thiết kế và phát triển phần lớn hệ thống backend.
  Xây dựng REST API phục vụ frontend và dashboard quản trị.
  Thiết kế cơ sở dữ liệu và các luồng nghiệp vụ đặt phòng.
  Xử lý xác thực, phân quyền và bảo mật dữ liệu.
  Xây dựng hệ thống quản lý phòng, đặt phòng và khách hàng.
  Tối ưu luồng xử lý dữ liệu giữa frontend và backend.
  Tham gia triển khai, kiểm thử và tích hợp hệ thống.

  **EN:** Developed the majority of the backend system.
  Built REST APIs for frontend and administrative dashboards.
  Designed database schemas and booking workflows.
  Implemented authentication, authorization, and security layers.
  Developed room, reservation, and customer management modules.
  Optimized data communication between frontend and backend.
  Participated in deployment, testing, and system integration.
- **image:**
  /storage/portfolio/jff4CEYZgL42LOE3BJxPYuzYEbkOjIRxp1TJB9eW.png
- **gallery_images:**

  - /uploads/portfolio/gallery/ot8boC0GuW25uE63uvG4iNyDZeOEvf687Ih7sZd3.jpg
  - /uploads/portfolio/gallery/Qj2jbjrZQyu34epkYGh4tROhxLFs6g8VdhnwDIGV.jpg
  - /uploads/portfolio/gallery/UrW84bKaxHdf9PnvdmadgRf1i7jCTDtA7OmbKKCm.jpg
  - /uploads/portfolio/gallery/FiBmN2aArAA8dOE0ABTn4IfEAGVH4H0wPklXgkFv.jpg
  - /uploads/portfolio/gallery/OopMDnkcrWxyaD6X6ycCLBZ5P4d7GVWmG2jQdO90.jpg
- **tech_stack:**

  - Laravel
  - PHP
  - MySQL
  - REST API
  - JWT Authentication
  - Tailwind CSS
  - React
  - JavaScript
  - Cloud Storage
- **features:**

  - **VI:** Đặt phòng trực tuyến

  **EN:** Online booking system
  - **VI:** Quản lý trạng thái đặt phòng

  **EN:** Reservation status tracking
  - **VI:** Quản lý dữ liệu vận hành tập trung

  **EN:** Centralized operational management
- **metrics:**

  -   - **label:** **VI:** Backend-Centric Architecture

  **EN:** Backend-Centric Architecture
    - **value:** **VI:** Phần lớn hệ thống nghiệp vụ được triển khai ở backend.

  **EN:** Most business logic was implemented on the backend layer.
  -   - **label:** **VI:** REST API Platform

  **EN:** REST API Platform
    - **value:** **VI:** Hệ thống API phục vụ frontend và dashboard quản trị.

  **EN:** REST API architecture supporting both customer-facing and admin interfaces.
  -   - **label:** **VI:** Booking Workflow Management

  **EN:** Booking Workflow Management
    - **value:** **VI:** Quản lý luồng đặt phòng và trạng thái vận hành tập trung.

  **EN:** Centralized booking workflow and reservation status management.
- **duration:**
  ~ 3 months
- **team:**
  6 people
- **status:**
  Completed
- **start_date:**
  2025-03-10
- **end_date:**
  2025-05-10
- **live_url:**
  https://lavishstay.dancru.cloud/
- **github_url:**
  https://github.com/markprovjp/LAVISHSTAY
- **sort_order:**
  1
- **is_active:**
  1
- **created_at:**
  2026-02-10 11:14:02
- **updated_at:**
  2026-05-30 04:01:28

#### Row #2

- **id:**
  2
- **title:**

  **VI:** Tổ chức sự kiện Thanh Hóa

  **EN:** Thanh Hoa Event Organization
- **slug:**

  **VI:** tổ-chức-sự-kiện-thanh-hóa

  **EN:** thanh-hoa-event-organization
- **category:**
  **VI:** Landing page + Admin
- **description:**

  **VI:** Website landing page

  **EN:** Website landing page
- **long_description:**

  **VI:** Website landing page quảng cáo cho cty liên quan đến tổ chức sự kiện: Đám cưới, đám hỏi, tiệc, sự kiện, đám tang, rạp ngoài trời,..

  **EN:** This website landing page advertises a company involved in event organization: weddings, engagements, parties, events, funerals, outdoor venues, etc.
- **content:**
  _Không có dữ liệu_
- **role:**

  **VI:** Nhà phát triển

  **EN:** Developer
- **responsibilities:**

  **VI:** Lên kế hoạch từ A -> Z, từ lên design cho tới thu thập thông tin và code web (no AI)

  **EN:** Planning from A to Z, from design to information gathering and web coding (no AI).
- **image:**
  /storage/portfolio/9kmvmCYYYQyKyjDb3rTAjkOj7HuX3jGtB9TWkDkl.png
- **gallery_images:**
  - /uploads/portfolio/gallery/R1PRFOJAxnX5PA3bD6SWmE0TLoOll3rRFq27dwdy.png
- **tech_stack:**

  - Laravel
  - HTML
  - CSS
  - JS
- **features:**
  _Không có dữ liệu_
- **metrics:**
  _Không có dữ liệu_
- **duration:**
  _Không có dữ liệu_
- **team:**
  _Không có dữ liệu_
- **status:**
  Live
- **start_date:**
  2024-10-07
- **end_date:**
  2025-01-15
- **live_url:**
  https://tochucsukienthanhhoa.vn/
- **github_url:**
  No git
- **sort_order:**
  5
- **is_active:**
  1
- **created_at:**
  2026-02-14 12:05:32
- **updated_at:**
  2026-05-30 03:32:11

#### Row #3

- **id:**
  3
- **title:**

  **VI:** Portfolio - Nền tảng Portfolio Full-stack cá nhân

  **EN:** Portfolio - Full-stack Personal Portfolio Platform
- **slug:**

  **VI:** portfolio

  **EN:** portfolio
- **category:**

  **VI:** Dự án cá nhân

  **EN:** Personal Project
- **description:**

  **VI:** Website portfolio full-stack được xây dựng nhằm trình bày dự án, kinh nghiệm và kỹ năng cá nhân, kết hợp hệ thống CMS quản trị nội dung đa ngôn ngữ bằng Laravel và FilamentPHP.

  **EN:** A full-stack portfolio platform built to showcase projects, experience, and technical skills, powered by a multilingual content management system using Laravel and FilamentPHP.
- **long_description:**

  **VI:** Phần lớn website portfolio cá nhân được xây dựng theo dạng tĩnh, khó mở rộng và khó quản lý nội dung khi số lượng dự án tăng lên.

  DanCru Portfolio được xây dựng như một nền tảng portfolio có backend quản trị riêng, cho phép quản lý dự án, kinh nghiệm, kỹ năng và nội dung đa ngôn ngữ từ một dashboard tập trung mà không cần chỉnh sửa source code trực tiếp.

  **EN:** Most personal portfolio websites are static and become difficult to maintain as the amount of content grows.

  DanCru Portfolio was designed as a portfolio platform with a dedicated administration system, allowing projects, experience, skills, and multilingual content to be managed from a centralized dashboard without directly editing source code.
- **content:**

  **VI:** DanCru Portfolio không chỉ là website giới thiệu cá nhân mà được xây dựng như một hệ thống quản lý nội dung hoàn chỉnh.

  Frontend được phát triển bằng React, TypeScript và Vite nhằm tối ưu hiệu năng tải trang và trải nghiệm người dùng. Phần giao diện sử dụng Tailwind CSS với hệ thống theme tùy chỉnh lấy cảm hứng từ phong cách UI của Valorant.

  Backend sử dụng Laravel 11 kết hợp FilamentPHP để xây dựng dashboard quản trị nội dung. Hệ thống cho phép quản lý dự án, kinh nghiệm làm việc, kỹ năng, thông tin cá nhân và nội dung đa ngôn ngữ Việt - Anh thông qua giao diện quản trị trực quan.

  Mục tiêu của dự án là tạo ra một nền tảng portfolio có khả năng mở rộng lâu dài thay vì một website tĩnh đơn giản, đồng thời đóng vai trò như trung tâm trình bày toàn bộ sản phẩm và hành trình phát triển cá nhân.

  **EN:** DanCru Portfolio was built as more than a personal website — it functions as a complete content management platform.

  The frontend was developed using React, TypeScript, and Vite to ensure fast performance and a modern user experience. The interface uses Tailwind CSS with a custom visual identity inspired by Valorant-style UI systems.

  The backend is powered by Laravel 11 and FilamentPHP, providing a dedicated administration panel for managing projects, experience, skills, personal information, and bilingual content.

  The goal was to create a scalable portfolio platform rather than a simple static website, serving as the central hub for showcasing professional work and technical growth.
- **role:**

  **VI:** Full-stack Developer / Product Designer

  **EN:** Full-stack Developer / Product Designer
- **responsibilities:**

  **VI:** Thiết kế kiến trúc frontend và backend cho toàn bộ hệ thống.
  Xây dựng giao diện portfolio bằng React, TypeScript và Tailwind CSS.
  Thiết kế theme tùy chỉnh lấy cảm hứng từ giao diện Valorant.
  Xây dựng CMS quản trị nội dung bằng Laravel và FilamentPHP.
  Phát triển hệ thống đa ngôn ngữ Việt - Anh.
  Thiết kế cấu trúc dữ liệu cho dự án, kinh nghiệm và kỹ năng.
  Tối ưu trải nghiệm người dùng, hiệu ứng chuyển động và khả năng responsive.
  Triển khai và vận hành hệ thống production.

  **EN:** Designed the overall frontend and backend architecture.
  Built the portfolio interface using React, TypeScript, and Tailwind CSS.
  Created a custom Valorant-inspired visual theme.
  Developed a CMS dashboard using Laravel and FilamentPHP.
  Implemented Vietnamese-English multilingual support.
  Designed content structures for projects, experience, and skills.
  Optimized responsiveness, animations, and user experience.
  Managed deployment and production operations.
- **image:**
  /storage/portfolio/1mXcLIenW4sxLHFVi39U3bgJgJC93OkC6fSENMaE.png
- **gallery_images:**
  - /uploads/portfolio/gallery/1FZZ1RWm8dZGDhO78yw2NSpnDSAx0gqxYWPKaprV.png
- **tech_stack:**

  - React
  - TypeScript
  - Vite
  - Tailwind CSS
  - Laravel 11
  - FilamentPHP v3
  - MySQL
  - REST API
  - Multilingual System
- **features:**

  - **VI:** Portfolio đa ngôn ngữ Việt - Anh

  **EN:** Vietnamese-English multilingual portfolio
  - **VI:** Quản lý kinh nghiệm làm việc

  **EN:** Experience management
  - **VI:** Dashboard quản trị tập trung

  **EN:** Centralized admin dashboard
  - **VI:** Hệ thống API Laravel phục vụ frontend

  **EN:** Laravel API backend
- **metrics:**

  -   - **label:** **VI:** Full-stack Architecture

  **EN:** Full-stack Architecture
    - **value:** **VI:** Frontend và backend được xây dựng tách biệt hoàn toàn.

  **EN:** Fully separated frontend and backend architecture.
  -   - **label:** **VI:** Multilingual CMS

  **EN:** Multilingual CMS
    - **value:** **VI:** Hỗ trợ quản lý nội dung song ngữ Việt - Anh.

  **EN:** Supports bilingual content management (Vietnamese and English).
  -   - **label:** **VI:** Admin-driven Content

  **EN:** Admin-driven Content
    - **value:** **VI:** Toàn bộ dữ liệu portfolio có thể quản lý từ dashboard.

  **EN:** Portfolio content is fully managed through an admin dashboard.
- **duration:**
  _Không có dữ liệu_
- **team:**
  1 people
- **status:**
  Live
- **start_date:**
  2026-01-03
- **end_date:**
  2026-05-30
- **live_url:**
  https://dancru.cloud/
- **github_url:**
  _Không có dữ liệu_
- **sort_order:**
  6
- **is_active:**
  1
- **created_at:**
  2026-02-14 12:20:35
- **updated_at:**
  2026-05-30 04:15:40

#### Row #4

- **id:**
  4
- **title:**

  **VI:** FaceConst - Nhà đẹp giá tốt

  **EN:** FaceConst - Beautiful homes at great prices
- **slug:**

  **VI:** faceconst---nhà-đẹp-giá-tốt

  **EN:** faceconst---beautiful-homes-at-great-prices
- **category:**

  **VI:** Mạng xã hội

  **EN:** A social network
- **description:**

  **VI:** Mạng xã hội dành riêng cho ngành xây dựng.

  **EN:** A social network dedicated to the construction industry.
- **long_description:**

  **VI:** Mạng xã hội dành riêng cho ngành xây dựng. Giao quen thuộc diện giống Facebook

  **EN:** A social network dedicated to the construction industry. Familiar interactions are similar to Facebook.
- **content:**
  _Không có dữ liệu_
- **role:**

  **VI:** Nhà phát triển

  **EN:** Developer
- **responsibilities:**

  **VI:** Tôi cùng với 4 người khác đảm nhiệm vai trò phát triển mạng xã hội này

  **EN:** I, along with four others, were responsible for developing this social network.
- **image:**
  /storage/portfolio/B9rzs7JG1wZSG5m3XSynW71ndTWH5V0Crc7JzMtN.png
- **gallery_images:**
  _Không có dữ liệu_
- **tech_stack:**

  - React
  - Laravel
  - TaiwindCss
  - Livewire
  - Alpine.js
- **features:**
  _Không có dữ liệu_
- **metrics:**
  _Không có dữ liệu_
- **duration:**
  _Không có dữ liệu_
- **team:**
  _Không có dữ liệu_
- **status:**
  Live
- **start_date:**
  2025-12-24
- **end_date:**
  2026-03-21
- **live_url:**
  https://nhadepgiatot.shinigami.io.vn/
- **github_url:**
  No public
- **sort_order:**
  3
- **is_active:**
  1
- **created_at:**
  2026-02-14 12:31:38
- **updated_at:**
  2026-05-30 03:32:19

### Raw table `certifications`

#### Row #1

- **id:**
  1
- **name:**

  **VI:** Sinh viên xuất sắc các kỳ & Thủ khoa đầu ra

  **EN:** Top student of each semester & Valedictorian of the graduating class
- **issuer:**

  **VI:** Cao đẳng FPT Polytechnic

  **EN:** FPT Polytechnic College
- **issue_date:**
  2024-05-20
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/mVrD0NfxQGbjPeMSYObRsjQj1I2ISjBWJDf2HgQT.jpg
- **sort_order:**
  1
- **is_active:**
  1
- **created_at:**
  2026-02-14 09:15:22
- **updated_at:**
  2026-05-30 01:10:08

#### Row #2

- **id:**
  2
- **name:**

  **VI:** Bằng khen giỏi và xuất sắc 6 kỳ

  **EN:** Certificates of excellence and outstanding performance for 6 terms.
- **issuer:**

  **VI:** Trường cao đẳng FPT Polytechnic

  **EN:** FPT Polytechnic College
- **issue_date:**
  2025-10-15
- **url:**
  grg
- **image:**
  /uploads/portfolio/oY7OgPe6lqvSUbZZDHLgX4O75LPwHzLYXEn5wn9g.jpg
- **sort_order:**
  2
- **is_active:**
  1
- **created_at:**
  2026-02-14 13:44:44
- **updated_at:**
  2026-02-15 03:35:08

#### Row #3

- **id:**
  3
- **name:**

  **VI:** Giải khuyến khích cuộc thi AI4Life

  **EN:** Encouragement Award in the AI4Life Competition
- **issuer:**

  **VI:** Trường cao đẳng FPT Polytechnic

  **EN:** FPT Polytechnic College
- **issue_date:**
  2025-08-09
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/ZzkIJv4T1Sv6l5BBnTUE6ve35O3NVQ8l0aHTJNMj.jpg
- **sort_order:**
  3
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:36:46
- **updated_at:**
  2026-02-15 03:37:12

#### Row #4

- **id:**
  4
- **name:**

  **VI:** Hiến máu tình nguyện

  **EN:** Voluntary blood donation
- **issuer:**

  **VI:** BCĐ vận động hiến máu tình nguyện tỉnh Thanh Hóa

  **EN:** Steering Committee for the Blood Donation Program of Thanh Hoa Province
- **issue_date:**
  2025-04-10
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/PWzaaL19ApStStgU3iWEPmXQqEtm32w47mc0ZQXH.jpg
- **sort_order:**
  4
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:39:40
- **updated_at:**
  2026-02-15 03:39:40

#### Row #5

- **id:**
  5
- **name:**

  **VI:** TOP 20 HACKATHON FRONTEND MASTER 2024

  **EN:** TOP 20 HACKATHON FRONTEND MASTER 2024
- **issuer:**

  **VI:** Hackathon x FPT

  **EN:** Hackathon x FPT
- **issue_date:**
  2024-06-04
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/1z44bIPb5KpEUQlR5dqHOU5MVGjM5Y1I4ShH3Fga.jpg
- **sort_order:**
  5
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:41:15
- **updated_at:**
  2026-02-15 03:41:15

#### Row #6

- **id:**
  6
- **name:**

  **VI:** Bậc thầy săn bug

  **EN:** Bug slayer
- **issuer:**

  **VI:** FPT

  **EN:** FPT
- **issue_date:**
  2025-04-08
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/j2yRgX4NEb6Lx7qx5NxuYlJzRo7n8fqxvqyI57Yn.jpg
- **sort_order:**
  6
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:42:45
- **updated_at:**
  2026-02-15 03:42:45

#### Row #7

- **id:**
  7
- **name:**

  **VI:** Giáo dục QP&AN

  **EN:** National Defense and Security Education
- **issuer:**

  **VI:** Trung tâm giáo dục Quốc phòng và An ninh Trường Đại học Hồng Đức

  **EN:** Center for National Defense and Security Education, Hong Duc University
- **issue_date:**
  2025-01-14
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/bBGS7NgWmBpEtZWwXghieyEoSYGc4j0c0X5PLiES.jpg
- **sort_order:**
  7
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:44:32
- **updated_at:**
  2026-02-15 03:44:32

#### Row #8

- **id:**
  8
- **name:**

  **VI:** Tình nguyện viên tại Giải Vô địch Quốc gia Việt  Nam VEX Robotics 2025

  **EN:** Volunteers at the Vietnam National Robotics Championship VEX 2025
- **issuer:**

  **VI:** Liên minh Thúc đẩy Giáo dục STEM

  **EN:** Alliance to Promote STEM Education
- **issue_date:**
  2025-01-16
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/R0QZ3u7PKCa1CFt0zXbC79MFPEXOP91rZ4alNqEU.png
- **sort_order:**
  8
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:48:04
- **updated_at:**
  2026-02-15 03:48:04

#### Row #9

- **id:**
  9
- **name:**

  **VI:** Kỹ năng lập trình PHP

  **EN:** PHP programming skills
- **issuer:**

  **VI:** FPT

  **EN:** FPT
- **issue_date:**
  2024-08-18
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/OsGgIi2mC7exmGKQMp5fw3PyjgVPbgIfknBi5EHq.png
- **sort_order:**
  9
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:50:17
- **updated_at:**
  2026-02-15 03:50:17

#### Row #10

- **id:**
  10
- **name:**

  **VI:** Trọng tài Trưởng Cuộc thi Robot VEX IQ (VIQRC) năm 2024-2025

  **EN:** Head Referee of the VEX IQ Robotics Competition (VIQRC) 2024-2025
- **issuer:**

  **VI:** REC Foundation

  **EN:** REC Foundation
- **issue_date:**
  2025-01-08
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/pfS2cAU2t8rJpeSN8m6sNId6Qj7LC4sTQxdWGhQ2.png
- **sort_order:**
  10
- **is_active:**
  1
- **created_at:**
  2026-02-15 03:53:56
- **updated_at:**
  2026-02-15 03:53:56

#### Row #11

- **id:**
  11
- **name:**

  **VI:** Gemini Certified Student

  **EN:** Gemini Certified Student
- **issuer:**

  **VI:** Google for Education

  **EN:** Google for Education
- **issue_date:**
  2026-02-15
- **url:**
  _Không có dữ liệu_
- **image:**
  /uploads/portfolio/gLqj3sSgQWsFwSCD2Iqt7aF2P02R4i45wsbU8c8K.png
- **sort_order:**
  11
- **is_active:**
  1
- **created_at:**
  2026-05-03 16:26:11
- **updated_at:**
  2026-05-30 01:08:15

### Raw table `translations`

_Không có dữ liệu._
