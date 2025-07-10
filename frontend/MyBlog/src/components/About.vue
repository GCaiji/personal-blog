
-<template>
  <div class="about-me-content">
    <h2>关于我</h2>
    <p>你好！我是一名热衷于技术和创新的开发者。我喜欢探索新的编程语言和框架，并致力于构建高效、用户友好的应用程序。</p>
    <p>在我的职业生涯中，我积累了丰富的经验，涵盖了前端开发（Vue.js, React）、后端开发（Python Flask, Node.js）、数据库管理（SQL, MongoDB）以及云计算平台（AWS, Azure）等多个领域。</p>
    <p>我坚信持续学习和分享知识的重要性。除了编码，我还喜欢阅读、旅行和摄影。我希望通过我的博客分享我的技术见解、项目经验和生活感悟。</p>
    <h3>我的技能</h3>
    <ul>
      <li>前端: Vue.js, React, JavaScript, HTML, CSS</li>
      <li>后端: Python (Flask), Node.js (Express)</li>
      <li>数据库: MySQL, PostgreSQL, MongoDB</li>
      <li>云平台: AWS, Azure</li>
      <li>版本控制: Git</li>
    </ul>
    <h3>联系我</h3>
    <p>如果你对我的项目感兴趣，或者想和我交流技术，欢迎通过以下方式联系我：</p>
    <ul>
      <li>Email: your.email@example.com</li>
      <li>GitHub: your_github_profile</li>
      <li>LinkedIn: your_linkedin_profile</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
.about-me-content {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  color: #333;
}

.about-me-content h2 {
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 2px solid #42b983;
  padding-bottom: 10px;
}

.about-me-content h3 {
  color: #2c3e50;
  margin-top: 25px;
  margin-bottom: 10px;
}

.about-me-content p {
  margin-bottom: 10px;
}

.about-me-content ul {
  list-style-type: disc;
  margin-left: 20px;
  margin-bottom: 10px;
}

.about-me-content ul li {
  margin-bottom: 5px;
}
</style>
