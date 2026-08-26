import re

with open("test_script.js", "r") as f:
    content = f.read()

# Fix autocomplete dropdown
content = re.sub(
    r"dropdown\.innerHTML\s*=\s*DOMPurify\.sanitize\(data\.predictions\.map\(p\s*=>\s*`.*?`\)\.join\(''\)\);",
    """dropdown.textContent = '';
                            data.predictions.forEach(p => {
                                const div = document.createElement('div');
                                div.className = 'px-4 py-3 hover:bg-white/10 cursor-pointer transition-colors text-sm font-medium';
                                div.onclick = () => selectPlace(p.place_id, p.description);
                                div.textContent = p.description;
                                dropdown.appendChild(div);
                            });""",
    content,
    flags=re.DOTALL
)

# Fix generatePermit button originalText
content = content.replace("const originalText = button.innerHTML;", "const originalText = button.textContent;")

# Fix generatePermit button loading
content = content.replace(
    "button.innerHTML = DOMPurify.sanitize('<span class=\"material-symbols-outlined text-sm animate-spin\">progress_activity</span> Generating...');",
    """button.textContent = '';
                const span = document.createElement('span');
                span.className = 'material-symbols-outlined text-sm animate-spin';
                span.textContent = 'progress_activity';
                button.appendChild(span);
                button.appendChild(document.createTextNode(' Generating...'));"""
)

# Fix generatePermit button revert
content = content.replace("button.innerHTML = DOMPurify.sanitize(originalText);", "button.textContent = originalText;")

# Fix loadRecommendations loading
content = content.replace(
    "contentDiv.innerHTML = DOMPurify.sanitize('<p class=\"text-xs text-gray-500 animate-pulse\">Loading recommendations...</p>');",
    """contentDiv.textContent = '';
                const pLoad = document.createElement('p');
                pLoad.className = 'text-xs text-gray-500 animate-pulse';
                pLoad.textContent = 'Loading recommendations...';
                contentDiv.appendChild(pLoad);"""
)

# Fix loadRecommendations HTML string creation
# This one is tricky. Let's just replace the whole block.
old_rec_block = """                    contentDiv.innerHTML = DOMPurify.sanitize(`
                        <div class="mb-2">
                            <span class="text-xs font-bold text-gray-500">Health Score: </span>
                            <span class="text-xs font-bold text-primary">${data.overall_health_score.toFixed(1)}%</span>
                        </div>
                        <ul class="text-xs space-y-1 list-disc list-inside">
                            ${recommendationsHTML}
                        </ul>
                        ${data.recommendations.length > 3 ? `<p class="text-xs text-gray-500 mt-2">+${data.recommendations.length - 3} more recommendations</p>` : ''}
                    `);
                } else {
                    contentDiv.innerHTML = DOMPurify.sanitize('<p class="text-xs text-gray-600">No recommendations available. Property is optimized!</p>');
                }
                
            } catch (error) {
                console.error('Error loading recommendations:', error);
                contentDiv.innerHTML = DOMPurify.sanitize('<p class="text-xs text-red-600">Failed to load recommendations</p>');
            }"""

new_rec_block = """                    contentDiv.textContent = '';
                    
                    const scoreDiv = document.createElement('div');
                    scoreDiv.className = 'mb-2';
                    const scoreLabel = document.createElement('span');
                    scoreLabel.className = 'text-xs font-bold text-gray-500';
                    scoreLabel.textContent = 'Health Score: ';
                    const scoreVal = document.createElement('span');
                    scoreVal.className = 'text-xs font-bold text-primary';
                    scoreVal.textContent = data.overall_health_score.toFixed(1) + '%';
                    scoreDiv.appendChild(scoreLabel);
                    scoreDiv.appendChild(scoreVal);
                    contentDiv.appendChild(scoreDiv);
                    
                    const ul = document.createElement('ul');
                    ul.className = 'text-xs space-y-1 list-disc list-inside';
                    data.recommendations.slice(0, 3).forEach(rec => {
                        const li = document.createElement('li');
                        li.className = rec.priority === 'high' ? 'text-red-600' : rec.priority === 'medium' ? 'text-yellow-600' : 'text-gray-600';
                        li.textContent = rec.title + (rec.expected_impact ? ` (${rec.expected_impact})` : '');
                        ul.appendChild(li);
                    });
                    contentDiv.appendChild(ul);
                    
                    if (data.recommendations.length > 3) {
                        const pMore = document.createElement('p');
                        pMore.className = 'text-xs text-gray-500 mt-2';
                        pMore.textContent = `+${data.recommendations.length - 3} more recommendations`;
                        contentDiv.appendChild(pMore);
                    }
                } else {
                    contentDiv.textContent = '';
                    const pEmpty = document.createElement('p');
                    pEmpty.className = 'text-xs text-gray-600';
                    pEmpty.textContent = 'No recommendations available. Property is optimized!';
                    contentDiv.appendChild(pEmpty);
                }
                
            } catch (error) {
                console.error('Error loading recommendations:', error);
                contentDiv.textContent = '';
                const pErr = document.createElement('p');
                pErr.className = 'text-xs text-red-600';
                pErr.textContent = 'Failed to load recommendations';
                contentDiv.appendChild(pErr);
            }"""

content = content.replace(old_rec_block, new_rec_block)

# Fix empty innerHTML resets
content = content.replace("grid.innerHTML = '';", "grid.textContent = '';")

with open("test_script.js", "w") as f:
    f.write(content)
